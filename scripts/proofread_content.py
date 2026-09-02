#!/usr/bin/env python3

"""Proofread canonical game prose one sentence at a time with a local Ollama model."""

import argparse
import hashlib
import http.client
import json
import re
import shutil
import subprocess
import sys
import time
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from main import error_path, load_schema  # noqa: E402


DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_RESULTS = ROOT / "benchmarks" / "results" / "proofread"
SYSTEM_PROMPT = """Be a strict proofreader, not an editor. Set fix to an empty string
unless the item has an objective spelling, grammar, agreement, or punctuation error.
Optional wording changes are forbidden. Fragments and commentary calls are valid.
Preserve facts, meaning, names, jargon, numbers, symbols, dashes, typography, and voice.
When necessary, put the full item with only the smallest correction in fix."""
RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["fix"],
    "properties": {"fix": {"type": "string"}},
}

# Names, labels, enum values, IDs, and paths are intentionally excluded.
PROSE_PATHS = (
    ("hook",),
    ("rules", "primary"),
    ("rules", "bullets", "*"),
    ("watch", "*", "text"),
    ("skill_shots", "*", "how"),
    ("skill_shots", "*", "value"),
    ("features", "*", "text"),
    ("shots", "*", "value"),
    ("strategy", "ahead"),
    ("strategy", "behind"),
    ("strategy", "key_decision"),
    ("danger", "*"),
    ("commentary", "*"),
    ("trivia", "*"),
    ("summary",),
    ("venue_notes", "*"),
)

SENTENCE_BOUNDARY = re.compile(
    r"[.!?]+(?:[\"'\u2019\u201d)\]]+)?(?=\s+[A-Z0-9\"'\u201c(\[]|$)"
)
WORD = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-/'][A-Za-z0-9]+)*")
NUMBER = re.compile(r"\d+(?:[.,]\d+)*(?:[KkMm%\u00d7xX])?")
ABBREVIATIONS = {
    "dr",
    "e.g",
    "i.e",
    "jr",
    "mr",
    "mrs",
    "ms",
    "no",
    "prof",
    "sr",
    "st",
    "vs",
}


def safe_component(value):
    component = re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-.")
    return component or "unnamed"


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def append_jsonl(path, value):
    with path.open("a", encoding="utf-8") as output:
        output.write(json.dumps(value, ensure_ascii=False) + "\n")


def parse_think(value):
    if value == "auto":
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    return value


def sentence_spans(text):
    """Return conservative sentence/fragment spans without splitting initials."""
    if not text:
        return []

    spans = []
    start = 0
    for match in SENTENCE_BOUNDARY.finditer(text):
        if match.end() < len(text) and match.group(0).startswith("."):
            prefix = text[: match.start() + 1]
            token_match = re.search(r"([A-Za-z](?:[A-Za-z.]*)?)\.$", prefix)
            token = token_match.group(1) if token_match else ""
            if token.lower() in ABBREVIATIONS or (
                len(token) == 1 and token.isupper()
            ):
                continue

        end = match.end()
        left = start
        while left < end and text[left].isspace():
            left += 1
        if left < end:
            spans.append((left, end))
        start = end

    left = start
    while left < len(text) and text[left].isspace():
        left += 1
    if left < len(text):
        spans.append((left, len(text)))
    return spans or [(0, len(text))]


def iter_matches(value, pattern, path=()):
    if not pattern:
        if isinstance(value, str) and value.strip():
            yield path, value
        return

    key, rest = pattern[0], pattern[1:]
    if key == "*":
        if isinstance(value, list):
            for index, item in enumerate(value):
                yield from iter_matches(item, rest, path + (index,))
    elif isinstance(value, dict) and key in value:
        yield from iter_matches(value[key], rest, path + (key,))


def iter_prose(value):
    seen = set()
    for pattern in PROSE_PATHS:
        for path, text in iter_matches(value, pattern):
            if path not in seen:
                seen.add(path)
                yield path, text


def get_path(value, path):
    for part in path:
        value = value[part]
    return value


def set_path(value, path, replacement):
    target = value
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = replacement


def display_path(path):
    rendered = "$"
    for part in path:
        rendered += f"[{part}]" if isinstance(part, int) else f".{part}"
    return rendered


def protected_terms(text):
    terms = []
    for index, match in enumerate(WORD.finditer(text)):
        token = match.group(0)
        has_internal_capital = any(char.isupper() for char in token[1:])
        if token.isupper() or has_internal_capital or (index > 0 and token[0].isupper()):
            terms.append(token)
    return Counter(terms)


def guardrail_violations(original, suggestion):
    violations = []
    if not suggestion.strip():
        violations.append("empty suggestion")
        return violations
    if "\n" in suggestion and "\n" not in original:
        violations.append("introduced a newline")
    if Counter(NUMBER.findall(original)) != Counter(NUMBER.findall(suggestion)):
        violations.append("changed numeric tokens")
    if protected_terms(original) != protected_terms(suggestion):
        violations.append("changed protected capitalized terms")
    for symbol in ("\u2192", "\u00d7", "\u2014", "\u2013"):
        if original.count(symbol) != suggestion.count(symbol):
            violations.append(f"changed {symbol!r} symbols")
    if abs(len(WORD.findall(original)) - len(WORD.findall(suggestion))) > 1:
        violations.append("added or removed multiple words")
    ratio = len(suggestion) / max(len(original), 1)
    if ratio < 0.6 or ratio > 1.5:
        violations.append("large length change")
    return violations


def replace_spans(text, replacements):
    for start, end, replacement in sorted(replacements, reverse=True):
        text = text[:start] + replacement + text[end:]
    return text


def schema_errors(data, schema):
    errors = sorted(
        Draft202012Validator(schema).iter_errors(data),
        key=lambda error: [str(part) for part in error.absolute_path],
    )
    return [f"{error_path(error)}: {error.message}" for error in errors]


class OllamaClient:
    """Small persistent HTTP client so sequential prompts reuse one warm model."""

    def __init__(self, base_url, timeout):
        parsed = urlsplit(base_url)
        if parsed.scheme != "http" or not parsed.hostname:
            raise ValueError("--ollama-url must be a local http:// URL")
        self.host = parsed.hostname
        self.port = parsed.port or 80
        self.prefix = parsed.path.rstrip("/")
        self.timeout = timeout
        self.connection = None

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def request(self, method, path, body=None):
        data = None if body is None else json.dumps(body).encode("utf-8")
        headers = {"Content-Type": "application/json"} if data is not None else {}
        last_error = None
        for _ in range(2):
            try:
                if self.connection is None:
                    self.connection = http.client.HTTPConnection(
                        self.host, self.port, timeout=self.timeout
                    )
                self.connection.request(method, self.prefix + path, data, headers)
                response = self.connection.getresponse()
                raw = response.read()
                if response.status >= 400:
                    detail = raw.decode("utf-8", errors="replace")
                    raise RuntimeError(f"Ollama returned HTTP {response.status}: {detail}")
                return json.loads(raw) if raw else {}
            except (OSError, http.client.HTTPException) as error:
                last_error = error
                self.close()
        raise RuntimeError(f"could not reach Ollama: {last_error}") from last_error

    def healthy(self):
        try:
            self.request("GET", "/api/tags")
            return True
        except RuntimeError:
            return False

    def warm(self, model, keep_alive):
        return self.request(
            "POST",
            "/api/generate",
            {"model": model, "prompt": "", "stream": False, "keep_alive": keep_alive},
        )

    def proofread(self, model, text, *, think, num_ctx, keep_alive):
        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Proofread:\n{text}"},
            ],
            "stream": False,
            "format": RESPONSE_SCHEMA,
            "keep_alive": keep_alive,
            "options": {
                "temperature": 0,
                "seed": 0,
                "num_ctx": num_ctx,
                "num_predict": 128,
            },
        }
        if think is not None:
            body["think"] = think
        started = time.monotonic()
        payload = self.request("POST", "/api/chat", body)
        elapsed = time.monotonic() - started
        content = (payload.get("message") or {}).get("content") or ""
        try:
            result = json.loads(content)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"Ollama returned invalid proofreading JSON: {error}") from error
        fix = result.get("fix")
        if not isinstance(fix, str):
            raise RuntimeError("Ollama proofreading response omitted string field 'fix'")
        suggestion = fix if fix else text
        metrics = {
            "elapsed_seconds": round(elapsed, 6),
            "prompt_tokens": payload.get("prompt_eval_count", 0),
            "output_tokens": payload.get("eval_count", 0),
        }
        return suggestion, metrics


def start_ollama(log_path):
    executable = shutil.which("ollama")
    if not executable:
        raise RuntimeError("Ollama is not running and the ollama executable was not found")
    log = log_path.open("a", encoding="utf-8")
    process = subprocess.Popen(
        [executable, "serve"],
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    return process, log


def ensure_server(client, log_path, startup_timeout, auto_start):
    if client.healthy():
        return None, None
    if not auto_start:
        raise RuntimeError("Ollama is not reachable; start it or pass --start-server")

    process, log = start_ollama(log_path)
    deadline = time.monotonic() + startup_timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            log.flush()
            log.close()
            raise RuntimeError(f"ollama serve exited with {process.returncode}")
        time.sleep(0.25)
        if client.healthy():
            return process, log
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
    log.close()
    raise RuntimeError(f"ollama serve did not become ready within {startup_timeout:g}s")


def stop_server(process, log):
    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
    if log is not None:
        log.close()


def cache_key(model, think, num_ctx, text):
    source = json.dumps(
        {
            "version": 2,
            "model": model,
            "think": think,
            "num_ctx": num_ctx,
            "system": SYSTEM_PROMPT,
            "text": text,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def cached_proofread(client, cache_dir, model, text, *, think, num_ctx, keep_alive):
    key = cache_key(model, think, num_ctx, text)
    path = cache_dir / f"{key}.json"
    if path.exists():
        cached = json.loads(path.read_text(encoding="utf-8"))
        return cached["suggestion"], cached.get("metrics", {}), True

    suggestion, metrics = client.proofread(
        model,
        text,
        think=think,
        num_ctx=num_ctx,
        keep_alive=keep_alive,
    )
    write_json(
        path,
        {"original": text, "suggestion": suggestion, "metrics": metrics},
    )
    return suggestion, metrics, False


def create_run_directory(results_dir, model, now=None):
    now = now or datetime.now(timezone.utc)
    base = Path(results_dir) / f"{now.strftime('%Y%m%dT%H%M%SZ')}--{safe_component(model)}"
    candidate = base
    suffix = 2
    while candidate.exists():
        candidate = base.with_name(f"{base.name}--{suffix}")
        suffix += 1
    candidate.mkdir(parents=True)
    return candidate


def selected_files(content_dir, requested):
    if requested:
        return [Path(path).resolve() for path in requested]
    return sorted(Path(content_dir).resolve().glob("*.yaml"))


def build_parser():
    parser = argparse.ArgumentParser(
        description="Proofread game content sentence-by-sentence with one warm Ollama model.",
    )
    parser.add_argument("--model", required=True, help="installed Ollama model tag")
    parser.add_argument("--file", action="append", help="YAML file to check; repeatable")
    parser.add_argument("--content-dir", type=Path, default=ROOT / "content")
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--start-server", action="store_true")
    parser.add_argument("--startup-timeout", type=float, default=30)
    parser.add_argument("--timeout", type=float, default=120)
    parser.add_argument("--keep-alive", default="30m")
    parser.add_argument("--num-ctx", type=int, default=1024)
    parser.add_argument(
        "--think",
        choices=("auto", "false", "true", "low", "medium", "high"),
        default="false",
    )
    parser.add_argument("--limit", type=int, help="stop after this many sentence prompts")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="atomically apply safe suggestions after schema validation",
    )
    parser.add_argument("--progress-every", type=int, default=25)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.limit is not None and args.limit < 1:
        print("ERROR: --limit must be positive", file=sys.stderr)
        return 2
    if args.limit is not None and args.apply:
        print("ERROR: --limit cannot be combined with --apply", file=sys.stderr)
        return 2

    files = selected_files(args.content_dir, args.file)
    if not files:
        print("ERROR: no YAML files selected", file=sys.stderr)
        return 2
    missing = [path for path in files if not path.is_file()]
    if missing:
        print(f"ERROR: file not found: {missing[0]}", file=sys.stderr)
        return 2

    run_dir = create_run_directory(args.results_dir.resolve(), args.model)
    cache_dir = args.results_dir.resolve() / "cache" / safe_component(args.model)
    cache_dir.mkdir(parents=True, exist_ok=True)
    corrected_dir = run_dir / "corrected"
    corrected_dir.mkdir()
    review_path = run_dir / "review.jsonl"
    schema = load_schema()
    think = parse_think(args.think)
    client = OllamaClient(args.ollama_url, args.timeout)
    server_process = server_log = None
    totals = Counter()
    started = time.monotonic()
    failure = None
    stop_requested = False

    print(f"Artifacts: {run_dir}", flush=True)
    print(f"Model: {args.model}; files: {len(files)}; applying: {args.apply}", flush=True)
    try:
        server_process, server_log = ensure_server(
            client,
            run_dir / "ollama-server.log",
            args.startup_timeout,
            args.start_server,
        )
        print("Loading model into memory...", flush=True)
        client.warm(args.model, args.keep_alive)
        print("Model ready; proofreading sequentially...", flush=True)

        for file_path in files:
            original_data = yaml.safe_load(file_path.read_text(encoding="utf-8"))
            if not isinstance(original_data, dict):
                raise RuntimeError(f"{file_path} does not contain a YAML object")
            original_errors = schema_errors(original_data, schema)
            if original_errors:
                raise RuntimeError(
                    f"{file_path.name} is invalid before proofreading: "
                    f"{'; '.join(original_errors)}"
                )
            corrected_data = deepcopy(original_data)
            changes_by_path = {}

            for field_path, field_text in iter_prose(original_data):
                replacements = []
                for sentence_index, (start, end) in enumerate(sentence_spans(field_text)):
                    if args.limit is not None and totals["checked"] >= args.limit:
                        stop_requested = True
                        break
                    original = field_text[start:end]
                    suggestion, metrics, was_cached = cached_proofread(
                        client,
                        cache_dir,
                        args.model,
                        original,
                        think=think,
                        num_ctx=args.num_ctx,
                        keep_alive=args.keep_alive,
                    )
                    changed = suggestion != original
                    violations = guardrail_violations(original, suggestion) if changed else []
                    safe = changed and not violations
                    if safe:
                        replacements.append((start, end, suggestion))

                    entry = {
                        "file": str(file_path),
                        "path": display_path(field_path),
                        "sentence": sentence_index,
                        "original": original,
                        "suggestion": suggestion,
                        "changed": changed,
                        "safe": safe,
                        "guardrail_violations": violations,
                        "cached": was_cached,
                        "metrics": metrics,
                    }
                    append_jsonl(review_path, entry)
                    totals["checked"] += 1
                    totals["cached"] += int(was_cached)
                    totals["changed"] += int(changed)
                    totals["safe_changes"] += int(safe)
                    totals["flagged_changes"] += int(changed and not safe)
                    if not was_cached:
                        totals["prompt_tokens"] += metrics.get("prompt_tokens", 0)
                        totals["output_tokens"] += metrics.get("output_tokens", 0)

                    if args.progress_every and totals["checked"] % args.progress_every == 0:
                        print(
                            f"Checked {totals['checked']} items; "
                            f"{totals['changed']} suggestions "
                            f"({totals['flagged_changes']} flagged)",
                            flush=True,
                        )
                if replacements:
                    changes_by_path[field_path] = replacements
                if stop_requested:
                    break

            for field_path, replacements in changes_by_path.items():
                current = get_path(original_data, field_path)
                set_path(corrected_data, field_path, replace_spans(current, replacements))

            errors = schema_errors(corrected_data, schema)
            if errors:
                raise RuntimeError(
                    f"safe suggestions made {file_path.name} invalid: {'; '.join(errors)}"
                )
            rendered = yaml.safe_dump(corrected_data, sort_keys=False, allow_unicode=True)
            (corrected_dir / file_path.name).write_text(rendered, encoding="utf-8")
            if args.apply and corrected_data != original_data:
                temporary = file_path.with_suffix(file_path.suffix + ".tmp")
                temporary.write_text(rendered, encoding="utf-8")
                temporary.replace(file_path)
                totals["files_modified"] += 1
            totals["files_completed"] += 1
            if stop_requested:
                break
    except (OSError, RuntimeError, ValueError, yaml.YAMLError) as error:
        failure = str(error)
        print(f"ERROR: {failure}", file=sys.stderr)
    except KeyboardInterrupt:
        failure = "interrupted by user"
        print("Interrupted; cached sentence results are safe to reuse.", file=sys.stderr)
    finally:
        client.close()
        stop_server(server_process, server_log)

    manifest = {
        "model": args.model,
        "provider": "ollama",
        "ollama_url": args.ollama_url,
        "keep_alive": args.keep_alive,
        "think": think,
        "num_ctx": args.num_ctx,
        "apply": args.apply,
        "files_selected": len(files),
        "complete": failure is None and not stop_requested,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "totals": dict(totals),
        "review": str(review_path),
        "corrected_dir": str(corrected_dir),
    }
    if failure:
        manifest["error"] = failure
    write_json(run_dir / "manifest.json", manifest)
    print(json.dumps(manifest["totals"], sort_keys=True))
    print(f"Manifest: {run_dir / 'manifest.json'}")
    return 1 if failure else 0


if __name__ == "__main__":
    raise SystemExit(main())
