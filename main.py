#!/usr/bin/env python3

import argparse
import difflib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path
from urllib.parse import urlencode

import yaml
from jsonschema import Draft202012Validator

from scripts.process_images import VARIANTS, process_images
from scripts.render import merge_pdfs, render_game


ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
RESEARCH = CONTENT / "research"
OUTPUT = ROOT / "output"
IMAGES = ROOT / "images"
DOWNLOADS = Path.home() / "Downloads"
GAME_LIST = CONTENT / "list_of_games.txt"
MANIFEST = ROOT / "pins.yaml"
SCHEMA = ROOT / "schema" / "game.schema.json"
RESEARCH_PROMPT_TEMPLATE = ROOT / "prompts" / "research-game.md"
FORMAT_PROMPT_TEMPLATE = ROOT / "prompts" / "format-game-yaml.md"
PIN_ID_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
IMAGE_SUFFIXES = {
    ".avif",
    ".bmp",
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
}


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


def normalized_game_id(game):
    """Normalize common display-name variants for research ID matching."""
    normalized = unicodedata.normalize("NFKD", game)
    normalized = normalized.encode("ascii", "ignore").decode("ascii").lower()
    normalized = normalized.replace("&", " and ")
    normalized = re.sub(r"['\u2019]", "", normalized)
    normalized = re.sub(r"\blimited edition\b", "le", normalized)
    normalized = re.sub(r"\bspecial edition\b", "se", normalized)
    normalized = re.sub(r"\bgold edition\b", "gold", normalized)
    normalized = re.sub(r"\bthe\b", " ", normalized)
    return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")


def matching_research_id(game, research_directory=None):
    research_directory = research_directory or RESEARCH
    research_ids = sorted(path.stem for path in research_directory.glob("*.md"))
    derived_id = suggested_research_id(game)
    if derived_id in research_ids:
        return derived_id

    normalized_id = normalized_game_id(game)
    if normalized_id in research_ids:
        return normalized_id

    game_tokens = set(normalized_id.split("-"))
    game_years = {token for token in game_tokens if re.fullmatch(r"\d{4}", token)}
    candidates = []
    for research_id in research_ids:
        comparable_id = normalized_game_id(research_id)
        research_tokens = set(comparable_id.split("-"))
        research_years = {
            token for token in research_tokens if re.fullmatch(r"\d{4}", token)
        }
        if game_years and research_years and game_years != research_years:
            continue

        overlap = len(game_tokens & research_tokens)
        if not overlap:
            continue
        precision = overlap / len(research_tokens)
        coverage = overlap / len(game_tokens)
        sequence = difflib.SequenceMatcher(
            None, normalized_id, comparable_id
        ).ratio()
        score = 0.65 * precision + 0.20 * sequence + 0.15 * coverage
        if precision >= 0.75 and score >= 0.72:
            candidates.append((score, research_id))

    candidates.sort(reverse=True)
    if not candidates:
        return None
    if len(candidates) > 1 and candidates[0][0] - candidates[1][0] < 0.05:
        return None
    return candidates[0][1]


def image_id_for_game(game, research_directory=None):
    return (
        matching_research_id(game, research_directory)
        or suggested_research_id(game)
    )


def first_game_without_image(
    game_list=None,
    images_directory=None,
    research_directory=None,
):
    game_list = game_list or GAME_LIST
    images_directory = images_directory or IMAGES
    games = [
        line.strip()
        for line in game_list.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    for game in games:
        image_id = image_id_for_game(game, research_directory)
        has_image = any(
            path.is_file() and path.stem == image_id
            for path in images_directory.glob(f"{image_id}.*")
        )
        if not has_image:
            return game
    return None


def black_and_white_pair(source, images_directory=None):
    images_directory = images_directory or IMAGES
    matches = sorted(
        path
        for path in images_directory.glob(f"{source.stem}-bw.*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )
    return matches[0] if matches else None


def color_images_without_black_and_white(images_directory=None):
    images_directory = images_directory or IMAGES
    try:
        paths = images_directory.iterdir()
    except OSError:
        return []

    color_images = sorted(
        path
        for path in paths
        if path.is_file()
        and not path.name.startswith(".")
        and not path.stem.endswith("-bw")
        and path.suffix.lower() in IMAGE_SUFFIXES
    )
    return [
        source
        for source in color_images
        if black_and_white_pair(source, images_directory) is None
    ]


def find_color_image(game, images_directory=None, research_directory=None):
    images_directory = images_directory or IMAGES
    supplied_path = Path(game).expanduser()
    if supplied_path.is_file():
        return supplied_path

    image_id = image_id_for_game(game, research_directory)
    matches = sorted(
        path
        for path in images_directory.glob(f"{image_id}.*")
        if path.is_file()
        and path.stem == image_id
        and path.suffix.lower() in IMAGE_SUFFIXES
    )
    return matches[0] if matches else None


def open_images_in_preview(paths):
    subprocess.run(
        ["open", "-a", "Preview", *(str(path) for path in paths)],
        check=True,
    )


def request_black_and_white_variant(variant_paths):
    print("\nBlack-and-white candidates:")
    names = list(VARIANTS)
    for index, name in enumerate(names, start=1):
        print(f"  {index}. {name}: {variant_paths[index - 1].name}")

    while True:
        try:
            answer = input(
                f"Choose the best variant [1-{len(names)}], "
                "enter its name, s to skip, or q to quit: "
            ).strip().lower()
        except EOFError:
            return "quit", None

        if answer in {"q", "quit"}:
            return "quit", None
        if answer in {"s", "skip"}:
            return "skip", None
        if answer in names:
            return "selected", variant_paths[names.index(answer)]
        if answer.isdigit() and 1 <= int(answer) <= len(names):
            return "selected", variant_paths[int(answer) - 1]
        print("Enter a listed number or name, s, or q.", file=sys.stderr)


def process_black_and_white_image(source):
    print(f"\nGenerating candidates for {source.name}...")
    with tempfile.TemporaryDirectory(prefix=f"{source.stem}-variants-") as directory:
        try:
            output_dir = process_images(source, Path(directory))
        except SystemExit as error:
            print(f"ERROR: {error}", file=sys.stderr)
            return "error"
        except (OSError, subprocess.CalledProcessError) as error:
            print(f"ERROR: could not generate image variants: {error}", file=sys.stderr)
            return "error"

        variant_paths = [
            output_dir / f"{source.stem}-{name}.png"
            for name in VARIANTS
        ]
        missing = [path for path in variant_paths if not path.is_file()]
        if missing:
            print(
                "ERROR: image processing did not create: "
                + ", ".join(path.name for path in missing),
                file=sys.stderr,
            )
            return "error"

        try:
            open_images_in_preview(variant_paths)
        except (OSError, subprocess.CalledProcessError) as error:
            print(f"ERROR: could not open Preview: {error}", file=sys.stderr)
            return "error"

        action, selected = request_black_and_white_variant(variant_paths)
        if action != "selected":
            return action

        destination = black_and_white_pair(source) or (
            IMAGES / f"{source.stem}-bw.png"
        )
        if not confirm_overwrite(destination):
            print("Black-and-white image not saved.", file=sys.stderr)
            return "skip"

        try:
            IMAGES.mkdir(parents=True, exist_ok=True)
            shutil.copy2(selected, destination)
        except OSError as error:
            print(
                f"ERROR: could not copy {selected} to {destination}: {error}",
                file=sys.stderr,
            )
            return "error"

        try:
            display_path = destination.relative_to(ROOT)
        except ValueError:
            display_path = destination
        variant_name = selected.stem[len(source.stem) + 1:]
        print(f"Saved {display_path} from the {variant_name} variant.")
        return "selected"


def interactive_black_and_white_images(game):
    game = game.strip()
    if game:
        source = find_color_image(game)
        if source is None:
            print(f"ERROR: no color image found for {game!r}.", file=sys.stderr)
            return 1
        sources = [source]
    else:
        sources = color_images_without_black_and_white()
        if not sources:
            print("Every color image already has a black-and-white pair.")
            return 0
        print(f"Found {len(sources)} color image(s) without black-and-white pairs.")

    had_error = False
    for source in sources:
        result = process_black_and_white_image(source)
        if result == "quit":
            break
        if result == "error":
            had_error = True
    return 1 if had_error else 0


def download_snapshot(downloads_directory=None):
    downloads_directory = downloads_directory or DOWNLOADS
    snapshot = {}
    try:
        paths = downloads_directory.iterdir()
    except OSError:
        return snapshot

    for path in paths:
        if path.name.startswith(".") or path.suffix.lower() == ".crdownload":
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        if path.is_file():
            snapshot[path] = (stat.st_size, stat.st_mtime_ns)
    return snapshot


def newest_download_since(snapshot, downloads_directory=None):
    downloads_directory = downloads_directory or DOWNLOADS
    candidates = []
    for path, signature in download_snapshot(downloads_directory).items():
        if snapshot.get(path) == signature:
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        birth_time = getattr(
            stat,
            "st_birthtime_ns",
            int(getattr(stat, "st_birthtime", 0) * 1_000_000_000),
        )
        candidates.append((max(stat.st_mtime_ns, birth_time), path))

    return max(candidates, default=(None, None))[1]


def google_image_search_url(game):
    return "https://www.google.com/search?" + urlencode({"tbm": "isch", "q": game})


def open_google_image_search(game):
    subprocess.run(
        ["open", "-a", "Google Chrome", google_image_search_url(game)],
        check=True,
    )


def interactive_game_image(game):
    game = game.strip()
    if not game:
        try:
            game = first_game_without_image()
        except OSError as error:
            print(f"ERROR: could not read game list {GAME_LIST}: {error}", file=sys.stderr)
            return 1

        if game is None:
            print(f"Every game in {GAME_LIST} already has an image.")
            return 0
        print(f"Selected first game without an image: {game}")

    if not game:
        print("ERROR: a game name is required.", file=sys.stderr)
        return 2
    if not DOWNLOADS.is_dir():
        print(f"ERROR: downloads directory does not exist: {DOWNLOADS}", file=sys.stderr)
        return 1

    before = download_snapshot()
    try:
        open_google_image_search(game)
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"ERROR: could not open Google Chrome: {error}", file=sys.stderr)
        return 1

    try:
        answer = input(
            "Download the desired image in Chrome, then press Enter to copy it "
            "(or enter q to cancel): "
        )
    except EOFError:
        answer = "q"
    if answer.strip().lower() in {"q", "quit"}:
        print("Image copy cancelled.", file=sys.stderr)
        return 0

    source = newest_download_since(before)
    if source is None:
        print(
            f"ERROR: no new completed file was found in {DOWNLOADS}.",
            file=sys.stderr,
        )
        return 1

    research_id = matching_research_id(game)
    image_id = image_id_for_game(game)
    if not image_id:
        print("ERROR: could not derive an image filename.", file=sys.stderr)
        return 1
    suffix = source.suffix.lower()
    destination = IMAGES / f"{image_id}{suffix}"
    if not confirm_overwrite(destination):
        print("Image not copied.", file=sys.stderr)
        return 0

    try:
        IMAGES.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    except OSError as error:
        print(f"ERROR: could not copy {source} to {destination}: {error}", file=sys.stderr)
        return 1

    id_source = "research" if research_id else "game name"
    print(f"Copied {source} to {destination.relative_to(ROOT)} ({id_source} ID).")
    return 0


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
        "--game-image",
        nargs="?",
        const="",
        metavar="NAME",
        help="Open a Google Image search and copy the newest download",
    )
    actions.add_argument(
        "--game-image-bw",
        nargs="?",
        const="",
        metavar="NAME",
        help="Generate and choose a black-and-white image variant",
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

    if args.game_image is not None:
        return interactive_game_image(args.game_image)

    if args.game_image_bw is not None:
        return interactive_black_and_white_images(args.game_image_bw)

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
