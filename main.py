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


def set_terminal_title(title, stream=None):
    stream = stream or sys.stderr
    if not stream.isatty():
        return False

    safe_title = re.sub(r"[\x00-\x1f\x7f]", "", title).strip()
    if not safe_title:
        return False

    stream.write(f"\033]0;{safe_title}\007")
    stream.flush()
    return True


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


def read_chatgpt_response(kind):
    print(
        f"\nPaste the ChatGPT {kind} response below. "
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


def human_questions(research):
    match = re.search(
        r"^## Questions for the humans\s*$\n(?P<body>.*?)(?=^## Sources\s*$|\Z)",
        research,
        flags=re.DOTALL | re.MULTILINE,
    )
    return match.group("body").strip() if match else ""


def human_resolutions(research):
    match = re.search(
        r"^## Human resolutions\s*$\n(?P<body>.*?)(?=^## Sources\s*$|\Z)",
        research,
        flags=re.DOTALL | re.MULTILINE,
    )
    return match.group("body").strip() if match else ""


def numbered_human_questions(research):
    questions = []
    current = []

    for line in human_questions(research).splitlines():
        if re.match(r"^\d+[.)]\s+\S", line):
            if current:
                questions.append("\n".join(current).strip())
            current = [line]
        elif current and re.match(r"^#{2,}\s+", line):
            questions.append("\n".join(current).strip())
            current = []
        elif current:
            current.append(line)

    if current:
        questions.append("\n".join(current).strip())
    return questions


def expand_multiple_choice_answer(question, answer):
    if not re.fullmatch(r"[A-Za-z]", answer):
        return answer

    choice = re.search(
        rf"^\s*{re.escape(answer)}[.)]\s+(?P<text>.+)$",
        question,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    if not choice:
        return answer
    return f"{answer.upper()}. {choice.group('text').strip()}"


def request_human_resolutions(research):
    questions = human_questions(research)
    numbered_questions = numbered_human_questions(research)
    print("\nHuman review is required before formatting.")
    if numbered_questions:
        print("\nAnswer each question with a choice letter or free text.")
        resolutions = []
        for index, question in enumerate(numbered_questions, start=1):
            print(f"\nQuestion {index} of {len(numbered_questions)}:\n")
            print(question)
            while True:
                try:
                    answer = input("Answer: ").strip()
                except EOFError:
                    return ""
                if answer:
                    break
                print("An answer is required; enter `unknown` if needed.", file=sys.stderr)
            answer = expand_multiple_choice_answer(question, answer)
            resolutions.append(f"{question}\n   **Human answer:** {answer}")
        return "\n\n".join(resolutions)

    if questions:
        print("\nThe research brief has no numbered questions:\n")
        print(questions)
    else:
        print("\nThe research response did not include a human-questions section.")
    print(
        "\nPaste the human answers or resolutions below. "
        "Enter `none` if no action is needed. "
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


def add_human_resolutions(research, resolutions):
    section = f"## Human resolutions\n\n{resolutions.strip()}\n\n"
    sources = re.search(r"^## Sources\s*$", research, flags=re.MULTILINE)
    if sources:
        return research[:sources.start()] + section + research[sources.start():]
    return research.rstrip() + "\n\n" + section.rstrip() + "\n"


def ensure_human_resolutions(research, path):
    if human_resolutions(research):
        print("Using the human resolutions already saved in the research brief.")
        return research

    resolutions = request_human_resolutions(research)
    if not resolutions:
        print("ERROR: human resolutions are required before formatting.", file=sys.stderr)
        return None

    research = add_human_resolutions(research, resolutions)
    path.write_text(research.rstrip() + "\n", encoding="utf-8")
    try:
        display_path = path.relative_to(ROOT)
    except ValueError:
        display_path = path
    print(f"Human resolutions saved to {display_path}")
    return research


def confirm_overwrite(path):
    if not path.exists():
        return True

    try:
        answer = input(f"{path} already exists. Overwrite? [y/N] ")
    except EOFError:
        answer = ""
    return answer.strip().lower() in {"y", "yes"}


def parse_json_response(response):
    fenced = re.fullmatch(
        r"\s*```(?:json)?\s*\n(?P<body>.*?)\n```\s*",
        response,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if fenced:
        response = fenced.group("body")
    return json.loads(response)


def format_research_interactively(research, research_id):
    output_path = CONTENT / f"{research_id}.yaml"
    if not confirm_overwrite(output_path):
        print("Formatted YAML not saved.", file=sys.stderr)
        return 1

    prompt = structured_formatting_prompt(research, expected_id=research_id)
    print("\n" + prompt)
    try:
        answer = input("\nCopy formatting prompt to clipboard? [y/N] ")
    except EOFError:
        answer = ""
    if answer.strip().lower() not in {"y", "yes"}:
        print("Formatting prompt not copied.", file=sys.stderr)
        return 0

    try:
        copy_to_clipboard(prompt)
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"ERROR: could not copy formatting prompt: {error}", file=sys.stderr)
        return 1
    print("Formatting prompt copied to clipboard.", file=sys.stderr)

    response = read_chatgpt_response("formatting")
    if not response:
        print("ERROR: no formatting response was provided.", file=sys.stderr)
        return 1

    try:
        data = parse_json_response(response)
    except json.JSONDecodeError as error:
        print(f"ERROR: formatting response is not valid JSON: {error}", file=sys.stderr)
        return 1
    if not isinstance(data, dict):
        print("ERROR: formatting response must be a JSON object.", file=sys.stderr)
        return 1

    errors = validation_errors(data, schema_validator())
    if data.get("id") != research_id:
        errors.append(
            f"$.id: expected {research_id!r}, got {data.get('id')!r}"
        )
    expected_image = f"images/{research_id}.jpg"
    if data.get("image") != expected_image:
        errors.append(
            f"$.image: expected {expected_image!r}, got {data.get('image')!r}"
        )
    if errors:
        print("ERROR: formatting response failed validation:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    output_path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    try:
        display_path = output_path.relative_to(ROOT)
    except ValueError:
        display_path = output_path
    print(f"Formatted YAML saved to {display_path}")
    return 0


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

    set_terminal_title(game)
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

    response = read_chatgpt_response("research")
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

    response = ensure_human_resolutions(response, path)
    if response is None:
        return 1
    return format_research_interactively(response, path.stem)


def interactive_game_format(research_id):
    research_id = research_id.strip()
    if not research_id:
        try:
            research_id = input("Research ID: ").strip()
        except EOFError:
            research_id = ""

    if not research_id:
        print("ERROR: a research ID is required.", file=sys.stderr)
        return 2
    if PIN_ID_PATTERN.fullmatch(research_id) is None:
        print(
            "ERROR: research ID must contain lowercase letters, numbers, and single hyphens.",
            file=sys.stderr,
        )
        return 2

    path = RESEARCH / f"{research_id}.md"
    try:
        research = path.read_text(encoding="utf-8")
    except OSError as error:
        print(f"ERROR: could not read research brief {path}: {error}", file=sys.stderr)
        return 1

    research = ensure_human_resolutions(research, path)
    if research is None:
        return 1
    return format_research_interactively(research, research_id)


def formatting_prompt(research):
    template = FORMAT_PROMPT_TEMPLATE.read_text(encoding="utf-8")
    return (
        template
        .replace("{{SCHEMA}}", json.dumps(load_schema(), indent=2))
        .replace("{{RESEARCH}}", research)
    )


def structured_formatting_prompt(research, expected_id=None):
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

    if expected_id:
        identity_rules = (
            f"- Set `id` exactly to `{expected_id}`.\n"
            f"- Set `image` exactly to `images/{expected_id}.jpg`.\n"
        )
        prompt = prompt.replace(
            "- Before answering, silently check the result against every schema constraint.\n",
            identity_rules
            + "- Before answering, silently check the result against every schema constraint.\n",
            1,
        )
    return prompt


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


def validation_errors(data, validator):
    errors = sorted(
        validator.iter_errors(data),
        key=lambda error: [str(part) for part in error.absolute_path],
    )
    return [
        f"{error_path(error)}: {error.message}"
        for error in errors
    ]


def validate_content(path: Path, validator):
    try:
        data = load_yaml(path)
    except yaml.YAMLError as error:
        return [f"invalid YAML: {error}"]

    return validation_errors(data, validator)


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
        "--game-format",
        nargs="?",
        const="",
        metavar="RESEARCH_ID",
        help="Format an existing content/research/<id>.md brief",
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

    if args.game_format is not None:
        return interactive_game_format(args.game_format)

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
