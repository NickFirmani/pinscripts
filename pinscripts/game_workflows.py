"""Guided workflows for adding and updating games in a printed binder."""

import difflib
import sys
import tempfile
from pathlib import Path

import yaml

from .ai import interactive_game_format, interactive_research_prompt
from .build import BuildInputError, build_print_packet, validate_all
from .content import PIN_ID_PATTERN, load_yaml, suggested_research_id
from .images import interactive_black_and_white_images, interactive_game_image
from .manual import (
    ManualError,
    insert_game,
    load_manual,
    suggested_insertion_index,
    write_manual,
)
from .paths import CONTENT, RESEARCH, ROOT
from .shot_labels import interactive_shot_labels
from .venue_notes import interactive_review_venue_notes


def ask_yes_no(prompt, default=True):
    suffix = " [Y/n] " if default else " [y/N] "
    try:
        answer = input(prompt + suffix).strip().lower()
    except EOFError:
        return False
    if not answer:
        return default
    return answer in {"y", "yes"}


def request_print_mode():
    """Ask how the packet should be rendered when generation begins."""
    while True:
        try:
            answer = input(
                "Generate the print packet in [c]olor or [b]lack-and-white [c]? "
            ).strip().lower()
        except EOFError:
            return None
        if answer in {"", "c", "color", "colour"}:
            return False
        if answer in {
            "b",
            "bw",
            "b&w",
            "black-and-white",
            "black and white",
        }:
            return True
        print("Enter 'c' for color or 'b' for black-and-white.", file=sys.stderr)


def _load_manual_or_report():
    try:
        return load_manual()
    except ManualError as error:
        print(f"ERROR: invalid printed-manual manifest: {error}", file=sys.stderr)
        return None


def _game_name(game_id):
    path = CONTENT / f"{game_id}.yaml"
    try:
        data = load_yaml(path)
    except (OSError, yaml.YAMLError):
        return game_id
    return data.get("name", game_id) if isinstance(data, dict) else game_id


def _describe_location(manual, index):
    if index:
        previous = manual.games[index - 1]
        left = f"{_game_name(previous.game_id)} (page {previous.pages[1]})"
    else:
        left = "the title page (page 1)"
    if index < len(manual.games):
        following = manual.games[index]
        right = f"{_game_name(following.game_id)} (page {following.pages[0]})"
    else:
        right = "the end of the manual"
    return left, right


def _resolve_game(manual, query):
    query = query.strip().lower()
    if not query:
        return None
    exact = [entry.game_id for entry in manual.games if entry.game_id == query]
    if exact:
        return exact[0]
    matches = []
    for entry in manual.games:
        name = _game_name(entry.game_id).lower()
        if query in entry.game_id or query in name:
            matches.append(entry.game_id)
    if len(matches) == 1:
        return matches[0]
    if matches:
        print("Matches:")
        for game_id in matches[:20]:
            entry = manual.entry(game_id)
            print(f"  {game_id:55} pages {entry.pages[0]}-{entry.pages[1]}")
        if len(matches) > 20:
            print(f"  ...and {len(matches) - 20} more")
    return None


def _request_game_id(manual, supplied):
    query = supplied.strip()
    while True:
        if not query:
            try:
                query = input("Game ID or part of its name: ").strip()
            except EOFError:
                return None
        game_id = _resolve_game(manual, query)
        if game_id:
            return game_id
        if query:
            print(f"No unique game matched {query!r}.", file=sys.stderr)
        query = ""


def _request_new_identity(description):
    description = description.strip()
    if not description:
        try:
            description = input("Game description: ").strip()
        except EOFError:
            description = ""
    if not description:
        print("ERROR: a game description is required.", file=sys.stderr)
        return None, None

    suggestion = suggested_research_id(description)
    try:
        game_id = input(f"Game ID [{suggestion}]: ").strip() or suggestion
    except EOFError:
        game_id = suggestion
    if PIN_ID_PATTERN.fullmatch(game_id) is None:
        print(
            "ERROR: the game ID must contain lowercase letters, numbers, and "
            "single hyphens.",
            file=sys.stderr,
        )
        return None, None
    return description, game_id


def _choose_insertion_index(manual, game_id):
    proposed = suggested_insertion_index(manual, game_id)
    left, right = _describe_location(manual, proposed)
    print(f"\nSuggested binder location: after {left}, before {right}.")
    if ask_yes_no("Use this location?"):
        return proposed

    while True:
        try:
            answer = input(
                "Insert after which game ID? Enter 'title' for the beginning: "
            ).strip()
        except EOFError:
            return None
        if answer.lower() == "title":
            return 0
        anchor = _resolve_game(manual, answer)
        if anchor:
            return manual.index(anchor) + 1
        print("Enter one unambiguous game ID or name.", file=sys.stderr)


def _ensure_game_assets(
    description,
    game_id,
    black_and_white,
    *,
    offer_shot_labels=False,
    rebuild_black_and_white=False,
):
    content_path = CONTENT / f"{game_id}.yaml"
    try:
        data = load_yaml(content_path)
    except (OSError, yaml.YAMLError) as error:
        print(f"ERROR: could not read {content_path}: {error}", file=sys.stderr)
        return False
    configured_image = data.get("image") if isinstance(data, dict) else None
    if not isinstance(configured_image, str) or not configured_image:
        print(f"ERROR: {content_path} has no valid image path.", file=sys.stderr)
        return False
    image = ROOT / configured_image
    if not image.is_file():
        print(f"\nThe required playfield image is missing: {image}")
        if not ask_yes_no("Open the guided image finder now?"):
            print("Run this add command again after adding the image.")
            return False
        if interactive_game_image(description, continue_batch=False):
            return False
    if not image.is_file():
        print(f"ERROR: the image is still missing: {image}", file=sys.stderr)
        return False

    if offer_shot_labels and ask_yes_no("Open the shot-label editor for this game?"):
        if interactive_shot_labels(game_id, continue_batch=False):
            return False

    if black_and_white:
        bw_image = image.with_name(f"{image.stem}-bw{image.suffix}")
        if rebuild_black_and_white or not bw_image.is_file():
            reason = "The playfield image changed." if rebuild_black_and_white else (
                f"The black-and-white image is missing: {bw_image.name}."
            )
            print(f"\n{reason}")
            if not ask_yes_no("Create the black-and-white image now?"):
                return False
            if interactive_black_and_white_images(game_id):
                return False
            if not bw_image.is_file():
                print(f"ERROR: the image is still missing: {bw_image}", file=sys.stderr)
                return False

    return True


def interactive_add_game(description=""):
    manual = _load_manual_or_report()
    if manual is None:
        return 1
    description, game_id = _request_new_identity(description)
    if not game_id:
        return 2
    if any(entry.game_id == game_id for entry in manual.games):
        print(
            f"ERROR: {game_id} is already in the manual; use make update instead.",
            file=sys.stderr,
        )
        return 1

    insertion_index = _choose_insertion_index(manual, game_id)
    if insertion_index is None:
        print("Add cancelled.")
        return 1
    proposed = insert_game(manual, game_id, insertion_index)
    pages = proposed.entry(game_id).pages
    print(f"Reserved page labels {pages[0]} and {pages[1]} (not saved yet).")

    content_path = CONTENT / f"{game_id}.yaml"
    if content_path.is_file():
        print(f"Resuming from existing content: {content_path.relative_to(ROOT)}")
    else:
        research_path = RESEARCH / f"{game_id}.md"
        if research_path.is_file():
            print(f"Resuming from existing research: {research_path.relative_to(ROOT)}")
            if not ask_yes_no("Format this existing research brief now?"):
                print("Add paused before content creation; run make add again to resume.")
                return 1
            if interactive_game_format(game_id):
                return 1
        else:
            if not ask_yes_no("Start the guided AI research flow now?"):
                print("Add paused before content creation; run make add again to resume.")
                return 1
            if interactive_research_prompt(description, research_id=game_id):
                return 1
        if not content_path.is_file():
            print("Add paused before formatted content was created; run it again to resume.")
            return 1
    if interactive_review_venue_notes(game_id) != 0:
        return 1

    if not _ensure_game_assets(
        description,
        game_id,
        True,
        offer_shot_labels=True,
    ):
        return 1
    if not validate_all([content_path]):
        return 1

    print(
        f"\nReady to add {_game_name(game_id)} on pages {pages[0]}-{pages[1]}."
    )
    if not ask_yes_no("Add this game and its page labels to manual.yaml?"):
        print("Add cancelled; manual.yaml was not changed.")
        return 1
    try:
        write_manual(proposed)
    except (ManualError, OSError, ValueError) as error:
        print(f"ERROR: could not update manual.yaml: {error}", file=sys.stderr)
        return 1
    print(f"\nAdded {game_id} to manual.yaml on pages {pages[0]}-{pages[1]}.")

    if not ask_yes_no("Generate the four-page add packet now?"):
        print(
            "manual.yaml is saved; no print packet was generated. "
            f"Use make update GAME=\"{game_id}\" when you are ready to print."
        )
        return 0
    black_and_white = request_print_mode()
    if black_and_white is None:
        print("manual.yaml is saved; print packet generation was cancelled.")
        return 0
    try:
        packet = build_print_packet(game_id, "add", proposed, black_and_white)
    except (BuildInputError, OSError, ValueError) as error:
        print(
            "ERROR: manual.yaml was saved, but the add packet could not be "
            f"generated: {error}",
            file=sys.stderr,
        )
        return 1
    print(f"Print {packet.relative_to(ROOT)} double-sided, flipping on the long edge.")
    return 0


def _update_description(game_id):
    data = load_yaml(CONTENT / f"{game_id}.yaml")
    metadata = data.get("metadata", {})
    return " ".join(
        str(value)
        for value in (
            data.get("name", game_id),
            metadata.get("manufacturer", ""),
            metadata.get("year", ""),
        )
        if value != ""
    )


def _refresh_content_with_review(game_id, description):
    """Build updated YAML separately, show its diff, then replace atomically."""
    content_path = CONTENT / f"{game_id}.yaml"
    original = content_path.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix=f".{game_id}-", dir=CONTENT) as directory:
        candidate = Path(directory) / content_path.name
        result = interactive_research_prompt(
            description,
            research_id=game_id,
            formatted_output_path=candidate,
        )
        if result:
            return False
        if not candidate.is_file():
            print("Content refresh was not completed; the original YAML is unchanged.")
            return False
        candidate_text = candidate.read_text(encoding="utf-8")
        diff = "".join(
            difflib.unified_diff(
                original.splitlines(keepends=True),
                candidate_text.splitlines(keepends=True),
                fromfile=str(content_path.relative_to(ROOT)),
                tofile=f"candidate/{content_path.name}",
            )
        )
        print("\nContent changes:\n")
        print(diff or "(No textual changes.)")
        if not ask_yes_no("Replace the current content with this candidate?"):
            print("Candidate discarded; the original YAML is unchanged.")
            return False
        candidate.replace(content_path)
    print(f"Updated {content_path.relative_to(ROOT)}")
    return True


def interactive_update_game(game=""):
    manual = _load_manual_or_report()
    if manual is None:
        return 1
    game_id = _request_game_id(manual, game)
    if not game_id:
        return 2
    entry = manual.entry(game_id)
    print(f"\nUpdating {_game_name(game_id)} (pages {entry.pages[0]}-{entry.pages[1]}).")
    print("  1. Refresh researched content")
    print("  2. Replace the playfield image")
    print("  3. Redo shot labels")
    print("  4. Review venue notes")
    print("  5. Build a packet from changes already made")
    try:
        actions = input("Choose steps (comma-separated) [5]: ").strip() or "5"
    except EOFError:
        actions = "5"
    requested = {part.strip() for part in actions.split(",") if part.strip()}
    if not requested <= {"1", "2", "3", "4", "5"}:
        print("ERROR: choose one or more numbers from 1 through 5.", file=sys.stderr)
        return 2

    try:
        description = _update_description(game_id)
    except (OSError, yaml.YAMLError, AttributeError) as error:
        print(f"ERROR: could not read {game_id} content: {error}", file=sys.stderr)
        return 1
    if "1" in requested and not _refresh_content_with_review(game_id, description):
        return 1
    image_replaced = False
    if "2" in requested:
        if interactive_game_image(description, continue_batch=False):
            return 1
        image_replaced = True
        if "3" not in requested and ask_yes_no(
            "The image changed. Redo its shot labels now?"
        ):
            requested.add("3")
    if "3" in requested and interactive_shot_labels(game_id, continue_batch=False):
        return 1
    if image_replaced and not _ensure_game_assets(
        description,
        game_id,
        True,
        rebuild_black_and_white=True,
    ):
        return 1
    if "4" in requested and interactive_review_venue_notes(game_id):
        return 1

    content_path = CONTENT / f"{game_id}.yaml"
    if not validate_all([content_path]):
        return 1
    if not ask_yes_no("Build the four-page update packet?"):
        print("Update packet cancelled.")
        return 0
    black_and_white = request_print_mode()
    if black_and_white is None:
        print("Update packet cancelled.")
        return 0
    if not _ensure_game_assets(
        description,
        game_id,
        black_and_white,
        rebuild_black_and_white=False,
    ):
        return 1
    try:
        packet = build_print_packet(game_id, "update", manual, black_and_white)
    except (BuildInputError, OSError, ValueError) as error:
        print(f"ERROR: could not build update packet: {error}", file=sys.stderr)
        return 1
    print(f"Print {packet.relative_to(ROOT)} double-sided, flipping on the long edge.")
    return 0
