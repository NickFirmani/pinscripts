#!/usr/bin/env python3

"""Benchmark the format-prompt phase against a local Ollama model."""

import argparse
import hashlib
import json
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from main import error_path, formatting_prompt, load_schema  # noqa: E402


DEFAULT_RESULTS = ROOT / "benchmarks" / "results" / "format-prompt"
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
MODES = ("structured-json", "direct-yaml")


def progress(message):
    print(message, file=sys.stderr, flush=True)


@contextmanager
def elapsed_heartbeat(interval, label="Waiting for Ollama"):
    """Print periodic elapsed-time updates around a blocking operation."""
    if interval <= 0:
        yield
        return

    stopped = threading.Event()
    started = time.monotonic()

    def emit_updates():
        while not stopped.wait(interval):
            elapsed = time.monotonic() - started
            progress(f"{label}... {elapsed:.0f}s elapsed")

    thread = threading.Thread(target=emit_updates, daemon=True)
    thread.start()
    try:
        yield
    finally:
        stopped.set()
        thread.join(timeout=interval)


def structured_formatting_prompt(research):
    """Adapt the production YAML prompt for schema-constrained JSON output."""
    prompt = formatting_prompt(research)
    replacements = (
        (
            "# Pinball Streaming Quick Reference YAML Formatter",
            "# Pinball Streaming Quick Reference Structured Formatter",
        ),
        (
            "Convert the research brief below into YAML for a one-page, live-commentary\n"
            "quick reference.",
            "Convert the research brief below into structured data for a one-page,\n"
            "live-commentary quick reference.",
        ),
        (
            "Return ONLY YAML that validates against the following JSON Schema.",
            "Return ONLY a JSON object that validates against the following JSON Schema.",
        ),
        (
            "source commentary in the YAML.",
            "source commentary in the output.",
        ),
        (
            "Do not wrap the YAML in a Markdown code fence or add text before or after it.",
            "Do not wrap the JSON object in a Markdown code fence or add text before or after it.",
        ),
    )

    for original, replacement in replacements:
        if original not in prompt:
            raise ValueError(
                "format prompt changed; could not adapt this instruction: "
                f"{original!r}"
            )
        prompt = prompt.replace(original, replacement, 1)

    return prompt


def prompt_for_mode(research, mode):
    if mode == "structured-json":
        return structured_formatting_prompt(research)
    if mode == "direct-yaml":
        return formatting_prompt(research)
    raise ValueError(f"unsupported mode: {mode}")


def parse_think(value):
    if value == "auto":
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    return value


def ollama_request(model, prompt, schema, mode, think, num_ctx, timeout, base_url):
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {
            "temperature": 0,
            "seed": 0,
            "num_ctx": num_ctx,
        },
    }
    if mode == "structured-json":
        body["format"] = schema
    if think is not None:
        body["think"] = think

    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/chat",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Ollama returned HTTP {error.code}: {detail}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"could not reach Ollama at {base_url}: {error.reason}") from error

    return payload, time.monotonic() - started


def parse_model_output(payload, mode):
    message = payload.get("message") or {}
    content = message.get("content") or ""
    if not content.strip():
        thinking = message.get("thinking") or ""
        detail = f"; thinking contained {len(thinking)} characters" if thinking else ""
        raise ValueError(f"Ollama returned empty message.content{detail}")

    if mode == "structured-json":
        return json.loads(content)
    return yaml.safe_load(content)


def schema_errors(data, schema):
    validator = Draft202012Validator(schema)
    errors = sorted(
        validator.iter_errors(data),
        key=lambda error: [str(part) for part in error.absolute_path],
    )
    return [f"{error_path(error)}: {error.message}" for error in errors]


def nanoseconds_to_seconds(value):
    if not isinstance(value, (int, float)):
        return None
    return round(value / 1_000_000_000, 6)


def response_metrics(payload, elapsed_seconds):
    metrics = {"client_elapsed_seconds": round(elapsed_seconds, 6)}
    for name in (
        "total_duration",
        "load_duration",
        "prompt_eval_duration",
        "eval_duration",
    ):
        converted = nanoseconds_to_seconds(payload.get(name))
        if converted is not None:
            metrics[name.replace("_duration", "_seconds")] = converted

    for name in ("prompt_eval_count", "eval_count"):
        if isinstance(payload.get(name), int):
            metrics[name] = payload[name]

    eval_count = payload.get("eval_count")
    eval_duration = payload.get("eval_duration")
    if isinstance(eval_count, int) and isinstance(eval_duration, (int, float)) and eval_duration:
        metrics["output_tokens_per_second"] = round(
            eval_count / (eval_duration / 1_000_000_000),
            3,
        )

    return metrics


def safe_component(value):
    component = re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-.")
    return component or "unnamed"


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def create_run_directory(results_dir, research_path, model, mode, now=None):
    now = now or datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    base = (
        Path(results_dir)
        / safe_component(research_path.stem)
        / f"{stamp}--{safe_component(model)}--{mode}"
    )
    candidate = base
    suffix = 2
    while candidate.exists():
        candidate = base.with_name(f"{base.name}--{suffix}")
        suffix += 1
    candidate.mkdir(parents=True)
    return candidate


def write_json(path, value):
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def build_parser():
    parser = argparse.ArgumentParser(
        description="Run the format-prompt phase against a local Ollama model.",
    )
    parser.add_argument("--model", required=True, help="Ollama model tag")
    parser.add_argument(
        "--research",
        type=Path,
        default=ROOT / "content" / "research" / "jaws.md",
        help="research brief (default: content/research/jaws.md)",
    )
    parser.add_argument(
        "--mode",
        choices=MODES,
        default="structured-json",
        help="output strategy (default: structured-json)",
    )
    parser.add_argument(
        "--think",
        choices=("auto", "false", "true", "low", "medium", "high"),
        default="false",
        help="Ollama thinking setting; GPT-OSS uses low/medium/high",
    )
    parser.add_argument("--num-ctx", type=int, default=16384)
    parser.add_argument("--timeout", type=float, default=900)
    parser.add_argument(
        "--progress-interval",
        type=float,
        default=10,
        help="seconds between progress messages; use 0 to disable (default: 10)",
    )
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    research_path = args.research.resolve()
    try:
        research = research_path.read_text(encoding="utf-8")
    except OSError as error:
        print(f"ERROR: could not read research brief: {error}", file=sys.stderr)
        return 2

    schema = load_schema()
    try:
        prompt = prompt_for_mode(research, args.mode)
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    run_dir = create_run_directory(
        args.results_dir.resolve(),
        research_path,
        args.model,
        args.mode,
    )
    (run_dir / "prompt.md").write_text(prompt, encoding="utf-8")

    report = {
        "model": args.model,
        "mode": args.mode,
        "research": str(research_path),
        "research_sha256": sha256_text(research),
        "prompt_sha256": sha256_text(prompt),
        "schema": str((ROOT / "schema" / "game.schema.json").resolve()),
        "think": parse_think(args.think),
        "num_ctx": args.num_ctx,
        "progress_interval": args.progress_interval,
        "valid": False,
        "validation_errors": [],
    }

    progress("Starting format benchmark")
    progress(f"  Model: {args.model}")
    progress(f"  Mode: {args.mode}")
    progress(f"  Research: {research_path}")
    progress(f"  Context: {args.num_ctx} tokens")
    progress(f"  Artifacts: {run_dir}")
    progress("Submitting request to Ollama...")

    interrupted = False
    try:
        with elapsed_heartbeat(args.progress_interval):
            payload, elapsed = ollama_request(
                model=args.model,
                prompt=prompt,
                schema=schema,
                mode=args.mode,
                think=parse_think(args.think),
                num_ctx=args.num_ctx,
                timeout=args.timeout,
                base_url=args.ollama_url,
            )
        progress(f"Response received after {elapsed:.1f}s; parsing output...")
        write_json(run_dir / "response.json", payload)
        report["metrics"] = response_metrics(payload, elapsed)
        data = parse_model_output(payload, args.mode)
        if not isinstance(data, dict):
            raise ValueError(
                f"model output must decode to an object, got {type(data).__name__}"
            )
        errors = schema_errors(data, schema)
        report["validation_errors"] = errors
        report["valid"] = not errors
        progress(
            "Schema validation passed."
            if report["valid"]
            else f"Schema validation found {len(errors)} error(s)."
        )
        (run_dir / "output.yaml").write_text(
            yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
    except KeyboardInterrupt:
        interrupted = True
        report["interrupted"] = True
        report["error"] = "interrupted by user"
        progress("Interrupted; writing the partial run report...")
    except (RuntimeError, ValueError, json.JSONDecodeError, yaml.YAMLError) as error:
        report["error"] = str(error)
        progress(f"Benchmark failed: {error}")

    write_json(run_dir / "report.json", report)
    print(f"Run artifacts: {run_dir}")
    if interrupted:
        print("Result: interrupted", file=sys.stderr)
        return 130
    if report["valid"]:
        print("Result: valid")
        return 0

    print("Result: invalid", file=sys.stderr)
    if report.get("error"):
        print(f"  - {report['error']}", file=sys.stderr)
    for error in report["validation_errors"]:
        print(f"  - {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
