"""AI-assisted research, prompting, review, and formatting workflows."""

import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

from .content import (
    PIN_ID_PATTERN,
    load_schema,
    schema_validator,
    suggested_research_id,
    validation_errors,
)
from .interaction import confirm_overwrite, read_chatgpt_response, set_terminal_title
from .paths import (
    CONTENT,
    FORMAT_PROMPT_TEMPLATE,
    RESEARCH,
    RESEARCH_PROMPT_TEMPLATE,
    ROOT,
)


def research_prompt(game):
    template = RESEARCH_PROMPT_TEMPLATE.read_text(encoding="utf-8")
    return template.replace("{{GAME}}", game)


def copy_to_clipboard(text):
    subprocess.run(["pbcopy"], input=text, text=True, check=True)


def request_research_path(game):
    suggestion = suggested_research_id(game)
    while True:
        try:
            research_id = input(f"Research ID [{suggestion}]: ").strip() or suggestion
        except EOFError:
            print("ERROR: a research ID is required.", file=sys.stderr)
            return None

        if PIN_ID_PATTERN.fullmatch(research_id) is None:
            print(
                "Research ID must contain lowercase letters, numbers, and "
                "single hyphens.",
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
                print(
                    "An answer is required; enter `unknown` if needed.",
                    file=sys.stderr,
                )
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
        print(
            "ERROR: human resolutions are required before formatting.",
            file=sys.stderr,
        )
        return None

    research = add_human_resolutions(research, resolutions)
    path.write_text(research.rstrip() + "\n", encoding="utf-8")
    try:
        display_path = path.relative_to(ROOT)
    except ValueError:
        display_path = path
    print(f"Human resolutions saved to {display_path}")
    return research


def parse_json_response(response):
    fenced = re.fullmatch(
        r"\s*```(?:json)?\s*\n(?P<body>.*?)\n```\s*",
        response,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if fenced:
        response = fenced.group("body")
    return json.loads(response)


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
            "Convert the research brief below into YAML for a one-page, "
            "live-commentary\n"
            "quick reference.",
            "Convert the research brief below into structured data for a one-page,\n"
            "live-commentary quick reference.",
        ),
        (
            "Return ONLY YAML that validates against the following JSON Schema.",
            "Return ONLY a JSON object that validates against the following "
            "JSON Schema.",
        ),
        ("source commentary in the YAML.", "source commentary in the output."),
        (
            "Do not wrap the YAML in a Markdown code fence or add text before "
            "or after it.",
            "Do not wrap the JSON object in a Markdown code fence or add text "
            "before or after it.",
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
            f"- Set `image` exactly to `images/{expected_id}.webp`.\n"
        )
        prompt = prompt.replace(
            "- Before answering, silently check the result against every schema "
            "constraint.\n",
            identity_rules
            + "- Before answering, silently check the result against every schema "
            "constraint.\n",
            1,
        )
    return prompt


def read_prompt_input(source):
    if source == "-":
        return sys.stdin.read()
    return Path(source).read_text(encoding="utf-8")


def print_format_prompt(source):
    research = read_prompt_input(source)
    print(formatting_prompt(research))
    return 0


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
        errors.append(f"$.id: expected {research_id!r}, got {data.get('id')!r}")
    expected_image = f"images/{research_id}.webp"
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
        answer = input("\nCopy prompt to clipboard? [Y/n] ")
    except EOFError:
        answer = "n"
    if answer.strip().lower() not in {"", "y", "yes"}:
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
            "ERROR: research ID must contain lowercase letters, numbers, and "
            "single hyphens.",
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
