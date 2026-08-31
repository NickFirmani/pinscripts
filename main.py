#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from scripts.process_images import process_images
from scripts.render import merge_pdfs, render_game


ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
OUTPUT = ROOT / "output"
MANIFEST = ROOT / "pins.yaml"
SCHEMA = ROOT / "schema" / "game.schema.json"
PROMPT_TEMPLATE = ROOT / "prompts" / "generate-game.md"


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def enabled_pins():
    manifest = load_yaml(MANIFEST)
    return [
        pin
        for pin in manifest.get("pins", [])
        if pin.get("enabled", True)
    ]


def load_schema():
    with SCHEMA.open("r", encoding="utf-8") as file:
        return json.load(file)


def schema_validator():
    schema = load_schema()

    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def generation_prompt(game):
    template = PROMPT_TEMPLATE.read_text(encoding="utf-8")
    return (
        template
        .replace("{{SCHEMA}}", json.dumps(load_schema(), indent=2))
        .replace("{{GAME}}", game)
    )


def error_path(error):
    path = "$"

    for part in error.absolute_path:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"

    return path


def validate_content(path: Path, validator):
    try:
        data = load_yaml(path)
    except yaml.YAMLError as error:
        return [f"invalid YAML: {error}"]

    errors = sorted(
        validator.iter_errors(data),
        key=lambda error: [str(part) for part in error.absolute_path],
    )

    return [
        f"{error_path(error)}: {error.message}"
        for error in errors
    ]


def content_for_enabled_pins():
    paths = []

    for pin in enabled_pins():
        path = CONTENT / f"{pin['id']}.yaml"

        if not path.exists():
            print(f"WARNING: missing content: {path}", file=sys.stderr)
            continue

        paths.append(path)

    return paths


def validate_all(paths):
    validator = schema_validator()
    valid = True

    for path in paths:
        errors = validate_content(path, validator)

        if errors:
            valid = False
            print(f"ERROR: validation failed: {path}", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        else:
            print(f"Validated {path}")

    return valid


def render(paths):
    for path in paths:
        render_game(path, OUTPUT / f"{path.stem}.pdf")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Validate and render pinball commentary sheets.",
    )
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument(
        "game",
        nargs="?",
        help="Game ID, e.g. playboy-bally-1978",
    )
    actions.add_argument(
        "--all",
        action="store_true",
        help="Validate and render every enabled pin",
    )
    actions.add_argument(
        "--binder",
        action="store_true",
        help="Validate and render enabled pins, then create binder.pdf",
    )
    actions.add_argument(
        "--prompt",
        metavar="GAME",
        help="Print a generation prompt with the current schema embedded",
    )
    actions.add_argument(
        "--process-images",
        metavar="SOURCE",
        type=Path,
        help="Generate print variants of a playfield image",
    )
    parser.add_argument(
        "--image-output-dir",
        metavar="DIRECTORY",
        type=Path,
        help="Output directory for --process-images",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.prompt:
        print(generation_prompt(args.prompt))
        return 0

    if args.process_images:
        process_images(args.process_images, args.image_output_dir)
        return 0

    if args.image_output_dir:
        parser.error("--image-output-dir requires --process-images")

    if args.game:
        paths = [CONTENT / f"{args.game}.yaml"]
        if not paths[0].exists():
            parser.error(f"no content file: {paths[0]}")
    elif args.all or args.binder:
        paths = content_for_enabled_pins()
    else:
        parser.print_help()
        return 0

    if not validate_all(paths):
        return 1

    render(paths)

    if args.binder:
        pdfs = [OUTPUT / f"{path.stem}.pdf" for path in paths]
        merge_pdfs(pdfs, OUTPUT / "binder.pdf")

    return 0


if __name__ == "__main__":
    sys.exit(main())
