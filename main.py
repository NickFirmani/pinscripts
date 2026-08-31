#!/usr/bin/env python3

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from scripts.process_images import process_images
from scripts.render import merge_pdfs, render_game


ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
RESEARCH = CONTENT / "research"
OUTPUT = ROOT / "output"
MANIFEST = ROOT / "pins.yaml"
SCHEMA = ROOT / "schema" / "game.schema.json"
RESEARCH_PROMPT_TEMPLATE = ROOT / "prompts" / "research-game.md"
FORMAT_PROMPT_TEMPLATE = ROOT / "prompts" / "format-game-yaml.md"
PIN_ID_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


class PinRegistryError(ValueError):
    pass


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_pin_registry():
    try:
        registry = load_yaml(MANIFEST)
    except yaml.YAMLError as error:
        raise PinRegistryError(f"invalid YAML: {error}") from error

    if not isinstance(registry, dict):
        raise PinRegistryError("the document must be a mapping")

    expected_keys = {"enabled", "disabled"}
    actual_keys = set(registry)
    if actual_keys != expected_keys:
        missing = sorted(expected_keys - actual_keys)
        extra = sorted(actual_keys - expected_keys)
        details = []
        if missing:
            details.append(f"missing keys: {', '.join(missing)}")
        if extra:
            details.append(f"unknown keys: {', '.join(extra)}")
        raise PinRegistryError("; ".join(details))

    for list_name in ("enabled", "disabled"):
        pin_ids = registry[list_name]
        if not isinstance(pin_ids, list):
            raise PinRegistryError(f"{list_name} must be a list")

        invalid_ids = [
            pin_id
            for pin_id in pin_ids
            if not isinstance(pin_id, str)
            or PIN_ID_PATTERN.fullmatch(pin_id) is None
        ]
        if invalid_ids:
            raise PinRegistryError(
                f"{list_name} contains invalid pin IDs: "
                + ", ".join(repr(pin_id) for pin_id in invalid_ids)
            )

        duplicates = sorted({
            pin_id
            for pin_id in pin_ids
            if pin_ids.count(pin_id) > 1
        })
        if duplicates:
            raise PinRegistryError(
                f"{list_name} contains duplicate pin IDs: "
                + ", ".join(duplicates)
            )

    overlap = sorted(set(registry["enabled"]) & set(registry["disabled"]))
    if overlap:
        raise PinRegistryError(
            "pin IDs cannot be both enabled and disabled: "
            + ", ".join(overlap)
        )

    return registry


def load_schema():
    with SCHEMA.open("r", encoding="utf-8") as file:
        return json.load(file)


def schema_validator():
    schema = load_schema()

    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def research_prompt(game):
    template = RESEARCH_PROMPT_TEMPLATE.read_text(encoding="utf-8")
    return template.replace("{{GAME}}", game)


def copy_to_clipboard(text):
    subprocess.run(
        ["pbcopy"],
        input=text,
        text=True,
        check=True,
    )


def suggested_research_id(game):
    return re.sub(r"[^a-z0-9]+", "-", game.lower()).strip("-")


def request_research_path(game):
    suggestion = suggested_research_id(game)
    while True:
        try:
            research_id = input(f"Research ID [{suggestion}]: ").strip() or suggestion
        except EOFError:
            print("ERROR: a research ID is required.", file=sys.stderr)
            return None

        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", research_id):
            print(
                "Research ID must contain lowercase letters, numbers, and single hyphens.",
                file=sys.stderr,
            )
            continue

        path = RESEARCH / f"{research_id}.md"
        if not path.exists():
            return path

        try:
            overwrite = input(f"{path} already exists. Overwrite? [y/N] ")
        except EOFError:
            overwrite = ""
        if overwrite.strip().lower() in {"y", "yes"}:
            return path

        print("Research response not saved.", file=sys.stderr)
        return None


def read_research_response():
    print(
        "\nPaste the ChatGPT research response below. "
        "Finish with a line containing only ::end (or press Ctrl-D):"
    )
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "::end":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def interactive_research_prompt(game):
    game = game.strip()
    if not game:
        try:
            game = input("Game description: ").strip()
        except EOFError:
            game = ""

    if not game:
        print("ERROR: a game description is required.", file=sys.stderr)
        return 2

    prompt = research_prompt(game)
    print(prompt)

    try:
        answer = input("\nCopy prompt to clipboard? [y/N] ")
    except EOFError:
        answer = ""

    if answer.strip().lower() not in {"y", "yes"}:
        print("Prompt not copied.", file=sys.stderr)
        return 0

    try:
        copy_to_clipboard(prompt)
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"ERROR: could not copy prompt to clipboard: {error}", file=sys.stderr)
        return 1

    print("Prompt copied to clipboard.", file=sys.stderr)
    path = request_research_path(game)
    if path is None:
        return 1

    response = read_research_response()
    if not response:
        print("ERROR: no research response was provided.", file=sys.stderr)
        return 1

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(response + "\n", encoding="utf-8")
    try:
        display_path = path.relative_to(ROOT)
    except ValueError:
        display_path = path
    print(f"Research response saved to {display_path}")
    return 0


def formatting_prompt(research):
    template = FORMAT_PROMPT_TEMPLATE.read_text(encoding="utf-8")
    return (
        template
        .replace("{{SCHEMA}}", json.dumps(load_schema(), indent=2))
        .replace("{{RESEARCH}}", research)
    )


def read_prompt_input(source):
    if source == "-":
        return sys.stdin.read()

    return Path(source).read_text(encoding="utf-8")


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


def content_for_selected_pins():
    registry = load_pin_registry()
    enabled = registry["enabled"]
    disabled = set(registry["disabled"])

    if enabled:
        missing = [
            pin_id
            for pin_id in enabled
            if not (CONTENT / f"{pin_id}.yaml").is_file()
        ]
        if missing:
            raise PinRegistryError(
                "enabled pin IDs have no content file: " + ", ".join(missing)
            )
        selected = enabled
    else:
        selected = sorted(
            path.stem
            for path in CONTENT.glob("*.yaml")
            if path.stem not in disabled
        )

    return [CONTENT / f"{pin_id}.yaml" for pin_id in selected]


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


def render(paths, black_and_white=False):
    output_suffix = "-bw" if black_and_white else ""

    for path in paths:
        render_game(
            path,
            OUTPUT / f"{path.stem}{output_suffix}.pdf",
            black_and_white,
        )


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
        help="Validate and render the pins selected by pins.yaml",
    )
    actions.add_argument(
        "--binder",
        action="store_true",
        help="Render the pins selected by pins.yaml, then create binder.pdf",
    )
    actions.add_argument(
        "--game-research",
        nargs="?",
        const="",
        metavar="DESCRIPTION",
        help="Print a research prompt, prompting for the description if omitted",
    )
    actions.add_argument(
        "--format-prompt",
        metavar="RESEARCH",
        help="Print the phase-two YAML prompt using a research file, or - for stdin",
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
    image_modes = parser.add_mutually_exclusive_group()
    image_modes.add_argument(
        "--color",
        dest="black_and_white",
        action="store_false",
        help="Use the image named in the game YAML (default)",
    )
    image_modes.add_argument(
        "--black-and-white",
        "--bw",
        dest="black_and_white",
        action="store_true",
        help="Use the image with -bw appended before its extension",
    )
    parser.set_defaults(black_and_white=False)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.game_research is not None:
        return interactive_research_prompt(args.game_research)

    if args.format_prompt:
        try:
            research = read_prompt_input(args.format_prompt)
        except OSError as error:
            parser.error(f"could not read research brief: {error}")

        print(formatting_prompt(research))
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
        try:
            paths = content_for_selected_pins()
        except PinRegistryError as error:
            print(f"ERROR: invalid {MANIFEST}: {error}", file=sys.stderr)
            return 1
    else:
        parser.print_help()
        return 0

    if not validate_all(paths):
        return 1

    render(paths, args.black_and_white)

    if args.binder:
        output_suffix = "-bw" if args.black_and_white else ""
        pdfs = [
            OUTPUT / f"{path.stem}{output_suffix}.pdf"
            for path in paths
        ]
        merge_pdfs(pdfs, OUTPUT / f"binder{output_suffix}.pdf")

    return 0


if __name__ == "__main__":
    sys.exit(main())
