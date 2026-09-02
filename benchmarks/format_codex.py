#!/usr/bin/env python3

"""Format research briefs with an authenticated Codex CLI session."""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pinscripts.ai import human_resolutions, structured_formatting_prompt  # noqa: E402
from pinscripts.content import error_path, load_schema  # noqa: E402


DEFAULT_RESULTS = ROOT / "benchmarks" / "results" / "format-prompt"
DEFAULT_APP_CLI = Path("/Applications/ChatGPT.app/Contents/Resources/codex")
RATE_LIMIT_MARKERS = (
    "rate limit",
    "rate_limit",
    "usage limit",
    "usage_limit",
    "insufficient quota",
)


def safe_component(value):
    component = re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-.")
    return component or "unnamed"


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def resolve_codex_cli(value=None):
    if value:
        candidate = Path(value).expanduser().resolve()
        if candidate.is_file():
            return candidate
        raise FileNotFoundError(f"Codex CLI not found: {candidate}")

    discovered = shutil.which("codex")
    if discovered and Path(discovered).is_file():
        return Path(discovered).resolve()
    if DEFAULT_APP_CLI.is_file():
        return DEFAULT_APP_CLI
    raise FileNotFoundError("could not find an installed Codex CLI")


def promotion_ready_research(research_dir, content_dir):
    ready = []
    skipped = []
    for path in sorted(Path(research_dir).glob("*.md")):
        destination = Path(content_dir) / f"{path.stem}.yaml"
        if destination.exists():
            skipped.append({"id": path.stem, "reason": "content exists"})
            continue

        research = path.read_text(encoding="utf-8")
        if not human_resolutions(research).strip():
            skipped.append({"id": path.stem, "reason": "no human resolutions"})
            continue
        ready.append(path)
    return ready, skipped


def create_run_directory(results_dir, research_id, model, effort, now=None):
    now = now or datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    base = (
        Path(results_dir)
        / research_id
        / f"{stamp}--{safe_component(model)}-{effort}--structured-json"
    )
    candidate = base
    suffix = 2
    while candidate.exists():
        candidate = base.with_name(f"{base.name}--{suffix}")
        suffix += 1
    candidate.mkdir(parents=True)
    return candidate


def schema_errors(data, schema):
    validator = Draft202012Validator(schema)
    errors = sorted(
        validator.iter_errors(data),
        key=lambda error: [str(part) for part in error.absolute_path],
    )
    return [f"{error_path(error)}: {error.message}" for error in errors]


def parse_event_usage(path):
    usage = {}
    if not path.exists():
        return usage
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "turn.completed":
            usage = event.get("usage") or {}
    return usage


def contains_rate_limit(*values):
    combined = "\n".join(value for value in values if value).lower()
    return any(marker in combined for marker in RATE_LIMIT_MARKERS)


def promote_yaml(data, destination):
    text = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(destination)
    return text


def format_one(
    research_path,
    *,
    codex_cli,
    model,
    effort,
    schema,
    schema_path,
    results_dir,
    content_dir,
    promote,
    retries,
    timeout,
    abort_event,
):
    research_id = research_path.stem
    if abort_event.is_set():
        return {"id": research_id, "status": "not started after rate limit"}

    research = research_path.read_text(encoding="utf-8")
    prompt = structured_formatting_prompt(research, expected_id=research_id)
    run_dir = create_run_directory(results_dir, research_id, model, effort)
    (run_dir / "prompt.md").write_text(prompt, encoding="utf-8")

    response_path = run_dir / "response.json"
    attempts = []
    started = time.monotonic()
    failure = None

    for attempt in range(1, retries + 2):
        if abort_event.is_set():
            failure = "not started after rate limit"
            break

        response_path.unlink(missing_ok=True)
        events_path = run_dir / f"events-attempt-{attempt}.jsonl"
        stderr_path = run_dir / f"stderr-attempt-{attempt}.log"
        command = [
            str(codex_cli),
            "exec",
            "--ephemeral",
            "--ignore-user-config",
            "--ignore-rules",
            "--sandbox",
            "read-only",
            "--json",
            "--model",
            model,
            "--config",
            f'model_reasoning_effort="{effort}"',
            "--output-schema",
            str(schema_path),
            "--output-last-message",
            str(response_path),
            "-",
        ]
        attempt_started = time.monotonic()
        try:
            with (
                events_path.open("w", encoding="utf-8") as events_file,
                stderr_path.open("w", encoding="utf-8") as stderr_file,
            ):
                completed = subprocess.run(
                    command,
                    cwd=ROOT,
                    input=prompt,
                    text=True,
                    stdout=events_file,
                    stderr=stderr_file,
                    timeout=timeout,
                    check=False,
                )
            returncode = completed.returncode
            failure = None if returncode == 0 else f"Codex exited with {returncode}"
        except subprocess.TimeoutExpired:
            returncode = None
            failure = f"Codex timed out after {timeout:g} seconds"

        events_text = events_path.read_text(encoding="utf-8", errors="replace")
        stderr_text = stderr_path.read_text(encoding="utf-8", errors="replace")
        attempts.append(
            {
                "attempt": attempt,
                "returncode": returncode,
                "elapsed_seconds": round(time.monotonic() - attempt_started, 3),
                "events": str(events_path),
                "stderr": str(stderr_path),
            }
        )

        if failure is None and response_path.exists():
            break
        if contains_rate_limit(events_text, stderr_text):
            abort_event.set()
            failure = "Codex usage or rate limit reached"
            break
        if attempt <= retries:
            time.sleep(min(10 * attempt, 30))

    report = {
        "id": research_id,
        "model": model,
        "provider": "openai",
        "authentication": "ChatGPT",
        "reasoning_effort": effort,
        "mode": "structured-json",
        "research": str(research_path.resolve()),
        "research_sha256": sha256_text(research),
        "prompt_sha256": sha256_text(prompt),
        "schema": str(schema_path.resolve()),
        "attempts": attempts,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "valid": False,
        "promoted": False,
        "validation_errors": [],
    }

    if failure:
        report["status"] = "failed"
        report["error"] = failure
        write_json(run_dir / "report.json", report)
        return {"id": research_id, "status": "failed", "error": failure, "run": str(run_dir)}

    try:
        data = json.loads(response_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        report["status"] = "failed"
        report["error"] = f"could not parse model response: {error}"
        write_json(run_dir / "report.json", report)
        return {
            "id": research_id,
            "status": "failed",
            "error": report["error"],
            "run": str(run_dir),
        }

    errors = schema_errors(data, schema) if isinstance(data, dict) else [
        f"$: expected object, got {type(data).__name__}"
    ]
    if isinstance(data, dict):
        if data.get("id") != research_id:
            errors.append(f"$.id: expected {research_id!r}, got {data.get('id')!r}")
        expected_image = f"images/{research_id}.jpg"
        if data.get("image") != expected_image:
            errors.append(
                f"$.image: expected {expected_image!r}, got {data.get('image')!r}"
            )
        (run_dir / "output.yaml").write_text(
            yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

    last_events = Path(attempts[-1]["events"])
    report["usage"] = parse_event_usage(last_events)
    report["validation_errors"] = errors
    report["valid"] = not errors

    destination = Path(content_dir) / f"{research_id}.yaml"
    if not errors and promote:
        if destination.exists():
            errors.append(f"destination already exists: {destination}")
            report["validation_errors"] = errors
            report["valid"] = False
        else:
            promote_yaml(data, destination)
            report["promoted"] = True
            report["destination"] = str(destination.resolve())

    report["status"] = "promoted" if report["promoted"] else (
        "valid" if report["valid"] else "invalid"
    )
    write_json(run_dir / "report.json", report)
    return {
        "id": research_id,
        "status": report["status"],
        "usage": report.get("usage", {}),
        "errors": errors,
        "run": str(run_dir),
    }


def build_parser():
    parser = argparse.ArgumentParser(
        description="Format promotion-ready research briefs with Codex CLI.",
    )
    parser.add_argument("--model", default="gpt-5.6-terra")
    parser.add_argument(
        "--effort",
        choices=("minimal", "low", "medium", "high", "xhigh"),
        default="medium",
    )
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--timeout", type=float, default=900)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--promote", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--codex-cli")
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.workers < 1:
        print("ERROR: --workers must be at least 1", file=sys.stderr)
        return 2
    if args.retries < 0:
        print("ERROR: --retries cannot be negative", file=sys.stderr)
        return 2

    research_paths, skipped = promotion_ready_research(
        ROOT / "content" / "research",
        ROOT / "content",
    )
    if args.limit is not None:
        research_paths = research_paths[: args.limit]

    print(f"Promotion-ready briefs: {len(research_paths)}", flush=True)
    print(f"Skipped briefs: {len(skipped)}", flush=True)
    print(f"Model: {args.model} ({args.effort})", flush=True)
    print(f"Workers: {args.workers}", flush=True)
    print(f"Promote: {args.promote}", flush=True)
    if args.dry_run:
        for path in research_paths:
            print(path.stem)
        return 0
    if not research_paths:
        return 0

    try:
        codex_cli = resolve_codex_cli(args.codex_cli)
    except FileNotFoundError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    auth = subprocess.run(
        [str(codex_cli), "login", "status"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if auth.returncode != 0:
        print("ERROR: Codex CLI is not authenticated", file=sys.stderr)
        print(auth.stderr.strip(), file=sys.stderr)
        return 2
    print(auth.stdout.strip() or "Codex authentication confirmed", flush=True)

    schema_path = ROOT / "schema" / "game.schema.json"
    schema = load_schema()
    Draft202012Validator.check_schema(schema)
    batch_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    batch_dir = (
        args.results_dir.resolve()
        / "batches"
        / f"{batch_stamp}--{safe_component(args.model)}-{args.effort}"
    )
    batch_dir.mkdir(parents=True)
    manifest_path = batch_dir / "manifest.json"
    manifest = {
        "model": args.model,
        "reasoning_effort": args.effort,
        "workers": args.workers,
        "promote": args.promote,
        "targets": [path.stem for path in research_paths],
        "skipped": skipped,
        "results": [],
        "complete": False,
    }
    write_json(manifest_path, manifest)

    abort_event = threading.Event()
    write_lock = threading.Lock()
    completed_count = 0
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                format_one,
                path,
                codex_cli=codex_cli,
                model=args.model,
                effort=args.effort,
                schema=schema,
                schema_path=schema_path,
                results_dir=args.results_dir.resolve(),
                content_dir=ROOT / "content",
                promote=args.promote,
                retries=args.retries,
                timeout=args.timeout,
                abort_event=abort_event,
            ): path
            for path in research_paths
        }
        for future in as_completed(futures):
            path = futures[future]
            try:
                result = future.result()
            except Exception as error:  # pragma: no cover - final safety net
                result = {"id": path.stem, "status": "failed", "error": str(error)}
            completed_count += 1
            usage = result.get("usage") or {}
            token_note = (
                f" input={usage.get('input_tokens', 0)}"
                f" output={usage.get('output_tokens', 0)}"
            ) if usage else ""
            print(
                f"[{completed_count}/{len(research_paths)}] "
                f"{result['id']}: {result['status']}{token_note}",
                flush=True,
            )
            with write_lock:
                manifest["results"].append(result)
                write_json(manifest_path, manifest)

    manifest["complete"] = not abort_event.is_set()
    manifest["rate_limit_reached"] = abort_event.is_set()
    manifest["summary"] = {
        status: sum(1 for result in manifest["results"] if result["status"] == status)
        for status in sorted({result["status"] for result in manifest["results"]})
    }
    write_json(manifest_path, manifest)
    print(f"Batch manifest: {manifest_path}", flush=True)
    print("Summary: " + json.dumps(manifest["summary"], sort_keys=True), flush=True)

    successful_status = "promoted" if args.promote else "valid"
    return 0 if all(
        result["status"] == successful_status for result in manifest["results"]
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
