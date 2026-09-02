"""Interactive review and focused rewriting of venue notes."""

import re
import shutil
import sys
import tempfile
from pathlib import Path

import yaml

from .paths import CONTENT


def replace_venue_notes_section(text, notes):
    lines = text.splitlines(keepends=True)
    start = next(
        (
            index
            for index, line in enumerate(lines)
            if re.match(r"^venue_notes\s*:", line)
        ),
        None,
    )
    if start is None:
        raise ValueError("missing top-level venue_notes field")

    end = len(lines)
    for index in range(start + 1, len(lines)):
        if re.match(r"^[A-Za-z_][A-Za-z0-9_-]*\s*:", lines[index]):
            end = index
            break

    rendered = yaml.safe_dump(
        {"venue_notes": notes},
        sort_keys=False,
        allow_unicode=True,
        width=88,
    )
    return "".join(lines[:start]) + rendered + "".join(lines[end:])


def write_text_atomically(path, text):
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix=f".{path.name}-",
        suffix=".tmp",
        dir=path.parent,
        delete=False,
    ) as temporary:
        temporary.write(text)
        temporary_path = Path(temporary.name)

    try:
        shutil.copymode(path, temporary_path)
        temporary_path.replace(path)
    except OSError:
        temporary_path.unlink(missing_ok=True)
        raise


def request_venue_note_action():
    while True:
        try:
            answer = input(
                "[Enter/a] accept, [r] remove, [e] edit, or [q] quit: "
            ).strip().lower()
        except EOFError:
            return "quit", None

        if answer in {"", "a", "accept", "k", "keep"}:
            return "accept", None
        if answer in {"r", "remove", "d", "delete"}:
            return "remove", None
        if answer in {"q", "quit"}:
            return "quit", None
        if answer in {"e", "edit"}:
            try:
                replacement = input("Edited note: ").strip()
            except EOFError:
                return "quit", None
            if not replacement:
                print("An edited note cannot be empty; use remove instead.")
                continue
            if len(replacement) > 300:
                print(
                    f"The edited note is {len(replacement)} characters; "
                    "the maximum is 300.",
                    file=sys.stderr,
                )
                continue
            return "edit", replacement

        print("Enter a, r, e, or q.", file=sys.stderr)


def review_venue_notes_file(path, position, total, stats):
    try:
        original = path.read_text(encoding="utf-8")
        data = yaml.safe_load(original)
    except (OSError, yaml.YAMLError) as error:
        print(f"ERROR: could not read {path}: {error}", file=sys.stderr)
        return "error"

    if (
        not isinstance(data, dict)
        or not isinstance(data.get("venue_notes"), list)
        or any(not isinstance(note, str) for note in data.get("venue_notes", []))
    ):
        print(f"ERROR: {path} has no valid venue_notes list.", file=sys.stderr)
        return "error"

    notes = data["venue_notes"]
    game_name = data.get("name", path.stem)
    print(f"\n=== [{position}/{total}] {game_name} ({path.stem}) ===")
    if not notes:
        print("No Venue Notes.")
        return "complete"

    reviewed = []
    changed = False
    for note_index, note in enumerate(notes):
        print(f"\n[{note_index + 1}/{len(notes)}] {note}")
        action, replacement = request_venue_note_action()
        if action == "accept":
            reviewed.append(note)
            stats["accepted"] += 1
        elif action == "remove":
            changed = True
            stats["removed"] += 1
        elif action == "edit":
            reviewed.append(replacement)
            changed = changed or replacement != note
            stats["edited"] += 1
        else:
            reviewed.extend(notes[note_index:])
            if changed:
                try:
                    updated = replace_venue_notes_section(original, reviewed)
                    write_text_atomically(path, updated)
                except (OSError, ValueError) as error:
                    print(f"ERROR: could not update {path}: {error}", file=sys.stderr)
                    return "error"
                stats["files_updated"] += 1
                print(f"Updated {path}")
            return "quit"

    if changed:
        try:
            updated = replace_venue_notes_section(original, reviewed)
            write_text_atomically(path, updated)
        except (OSError, ValueError) as error:
            print(f"ERROR: could not update {path}: {error}", file=sys.stderr)
            return "error"
        stats["files_updated"] += 1
        print(f"Updated {path}")
    else:
        print("No changes.")
    return "complete"


def interactive_review_venue_notes(game):
    game = game.strip()
    if game:
        supplied_path = Path(game).expanduser()
        if supplied_path.is_file():
            paths = [supplied_path]
        else:
            game_id = game.removesuffix(".yaml")
            path = CONTENT / f"{game_id}.yaml"
            if not path.is_file():
                print(f"ERROR: no content file: {path}", file=sys.stderr)
                return 1
            paths = [path]
    else:
        paths = sorted(CONTENT.glob("*.yaml"))
        if not paths:
            print(f"ERROR: no content files found in {CONTENT}.", file=sys.stderr)
            return 1

    stats = {"accepted": 0, "removed": 0, "edited": 0, "files_updated": 0}
    had_error = False
    for position, path in enumerate(paths, start=1):
        result = review_venue_notes_file(path, position, len(paths), stats)
        if result == "quit":
            break
        if result == "error":
            had_error = True

    print(
        "\nVenue Notes review: "
        f"{stats['accepted']} accepted, "
        f"{stats['removed']} removed, "
        f"{stats['edited']} edited; "
        f"{stats['files_updated']} file(s) updated."
    )
    return 1 if had_error else 0
