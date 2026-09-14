"""Guided workflows for reusable, location-neutral catalog games."""

from contextlib import contextmanager
from dataclasses import replace
import difflib
import hashlib
import sys
import tempfile
from pathlib import Path

import yaml

from .ai import interactive_game_format, interactive_research_prompt
from .binder import (
    BinderError,
    SourceOverride,
    add_game,
    binders_containing,
    load_binder,
    mark_manually_curated,
    mutate_binder,
    replace_entry,
)
from .build import BuildInputError, build_print_packet, validate_all, validate_game_contexts
from .catalog import (
    catalog_by_id,
    match_imported_game,
    resolve_game,
    similar_catalog_games,
)
from .content import PIN_ID_PATTERN, image_reference, load_yaml, suggested_research_id
from .images import interactive_black_and_white_images, interactive_game_image
from .locks import claim_lock
from .paths import CONTENT, OUTPUT, RESEARCH, ROOT
from .shot_labels import interactive_shot_labels, shot_label_issue


@contextmanager
def _claim_add_game(game_id, lock_directory=None):
    """Claim one game workflow without blocking another terminal."""
    with claim_lock(
        f"add-{game_id}",
        blocking=False,
        lock_directory=lock_directory,
    ) as claimed:
        yield claimed


def _pending_lock_name(binder_id, pending):
    digest = hashlib.sha256(pending.key.encode("utf-8")).hexdigest()[:16]
    return f"pending-{binder_id}-{digest}"


@contextmanager
def _claim_next_pending_game(binder_id, lock_directory=None):
    """Claim the first currently pending game not owned by another worker."""
    binder = load_binder(binder_id)
    for candidate in binder.pending_games:
        with claim_lock(
            _pending_lock_name(binder_id, candidate),
            blocking=False,
            lock_directory=lock_directory,
        ) as claimed:
            if not claimed:
                continue
            latest = load_binder(binder_id)
            pending = next(
                (item for item in latest.pending_games if item.key == candidate.key),
                None,
            )
            if pending is None:
                continue
            yield pending
            return
    yield None


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


def _game_name(game_id):
    path = CONTENT / f"{game_id}.yaml"
    try:
        data = load_yaml(path)
    except (OSError, yaml.YAMLError):
        return game_id
    return data.get("name", game_id) if isinstance(data, dict) else game_id


def _request_game_id(supplied):
    query = supplied.strip()
    while True:
        if not query:
            try:
                query = input("Game ID or part of its name: ").strip()
            except EOFError:
                return None
        game = resolve_game(query)
        if game:
            return game.game_id
        if query:
            print(f"No unique game matched {query!r}.", file=sys.stderr)
        query = ""


def _select_similar_game(description, *, manufacturer=None, year=None):
    candidates = similar_catalog_games(
        description,
        manufacturer=manufacturer,
        year=year,
    )
    if not candidates:
        return None
    print("\nClosely named catalog games:")
    for index, game in enumerate(candidates, start=1):
        print(
            f"  {index}. {game.name} — {game.manufacturer} {game.year or ''} "
            f"[{game.game_id}]"
        )
    while True:
        try:
            answer = input(
                "Select an existing game number, or press Enter to create a new one: "
            ).strip()
        except EOFError:
            return None
        if not answer:
            return None
        if answer.isdigit() and 1 <= int(answer) <= len(candidates):
            return candidates[int(answer) - 1]
        print(f"Enter a number from 1 through {len(candidates)}, or press Enter.")


def _request_new_identity(description, *, check_similar=True):
    description = description.strip()
    if not description:
        try:
            description = input("Game description: ").strip()
        except EOFError:
            description = ""
    if not description:
        print("ERROR: a game description is required.", file=sys.stderr)
        return None, None

    if check_similar:
        existing = _select_similar_game(description)
        if existing is not None:
            return description, existing.game_id

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
    image = ROOT / image_reference(game_id)
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

    if offer_shot_labels:
        issue = shot_label_issue(data)
        if issue:
            print(f"\nShot labels need attention: {issue}.")
            if ask_yes_no("Open the shot-label editor for this game?"):
                if interactive_shot_labels(game_id, continue_batch=False):
                    return False
        else:
            print("Shot labels are already current.")

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


def _resume_add_game(description, game_id):
    content_path = CONTENT / f"{game_id}.yaml"
    if content_path.is_file():
        print(f"Resuming from existing content: {content_path.relative_to(ROOT)}")
    else:
        research_path = RESEARCH / f"{game_id}.md"
        if research_path.is_file():
            print(f"Resuming from existing research: {research_path.relative_to(ROOT)}")
            if not ask_yes_no("Format this existing research brief now?"):
                print("Add paused before content creation; rerun this command to resume.")
                return 1
            if interactive_game_format(game_id):
                return 1
        else:
            if not ask_yes_no("Start the guided AI research flow now?"):
                print("Add paused before content creation; rerun this command to resume.")
                return 1
            if interactive_research_prompt(description, research_id=game_id):
                return 1
        if not content_path.is_file():
            print("Add paused before formatted content was created; run it again to resume.")
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
    print(f"Catalog game {_game_name(game_id)} is ready as {game_id}.")
    return 0


def _override_pending(binder, pending, action, catalog_id=None, reason=None):
    override = SourceOverride(pending, action, catalog_id, reason or None)
    overrides = [
        item for item in binder.source_overrides if item.imported.key != pending.key
    ]
    overrides.append(override)
    return mark_manually_curated(
        replace(binder, source_overrides=tuple(overrides))
    )


def _finish_pending_game(
    binder_id,
    pending,
    *,
    catalog_id=None,
    override_action=None,
    reason=None,
):
    """Commit one queue result against the latest binder under its write lock."""
    catalog = catalog_by_id()

    def finish(binder):
        if not any(item.key == pending.key for item in binder.pending_games):
            return binder
        updated = replace(
            binder,
            pending_games=tuple(
                item for item in binder.pending_games if item.key != pending.key
            ),
        )
        if catalog_id is not None:
            try:
                existing = updated.entry(catalog_id)
            except BinderError:
                updated = add_game(updated, catalog_id, catalog)
            else:
                if not existing.present:
                    updated = replace_entry(updated, replace(existing, present=True))
        if override_action is not None:
            updated = _override_pending(
                updated,
                pending,
                override_action,
                catalog_id,
                reason,
            )
        return updated

    return mutate_binder(binder_id, finish)


def _optional_reason(prompt):
    try:
        return input(prompt).strip() or None
    except EOFError:
        return None


def _process_pending_game(binder_id, pending):
    print(f"\nClaimed from {binder_id}: {pending.description}")
    catalog = catalog_by_id()
    exact = match_imported_game(pending, catalog)
    if exact is not None:
        _finish_pending_game(binder_id, pending, catalog_id=exact.game_id)
        print(f"Attached existing catalog game {exact.game_id}.")
        return 0, True

    similar = _select_similar_game(
        pending.name,
        manufacturer=pending.manufacturer,
        year=pending.year,
    )
    if similar is not None:
        reason = _optional_reason("Reason for this match (optional): ")
        _finish_pending_game(
            binder_id,
            pending,
            catalog_id=similar.game_id,
            override_action="replace",
            reason=reason,
        )
        print(f"Mapped the imported listing to {similar.game_id}.")
        return 0, True

    while True:
        try:
            answer = input(
                "[a]dd a new catalog game, [m]atch an existing game, "
                "[i]gnore this listing, or [r]elease it: "
            ).strip().lower()
        except EOFError:
            answer = "r"
        if answer in {"r", "release", "q", "quit"}:
            print("Released the game back to the pending queue.")
            return 0, False
        if answer in {"i", "ignore"}:
            reason = _optional_reason("Reason for ignoring it (optional): ")
            _finish_pending_game(
                binder_id,
                pending,
                override_action="ignore",
                reason=reason,
            )
            print("Saved an ignore override; future syncs will not requeue it.")
            return 0, True
        if answer in {"m", "match"}:
            try:
                query = input("Catalog game ID or unambiguous name: ").strip()
            except EOFError:
                query = ""
            game = resolve_game(query)
            if game is None:
                print(f"No unique catalog game matched {query!r}.", file=sys.stderr)
                continue
            reason = _optional_reason("Reason for this correction (optional): ")
            _finish_pending_game(
                binder_id,
                pending,
                catalog_id=game.game_id,
                override_action="replace",
                reason=reason,
            )
            print(f"Mapped the imported listing to {game.game_id}.")
            return 0, True
        if answer not in {"a", "add", ""}:
            print("Choose add, match, ignore, or release.", file=sys.stderr)
            continue

        description, game_id = _request_new_identity(
            pending.description,
            check_similar=False,
        )
        if not game_id:
            return 2, False
        with _claim_add_game(game_id) as claimed:
            if not claimed:
                print(
                    f"Another game workflow is already working on {game_id}; "
                    "released this listing back to the queue."
                )
                return 0, False
            result = _resume_add_game(description, game_id)
        if result:
            return result, False
        exact = match_imported_game(pending, catalog_by_id())
        needs_override = exact is None or exact.game_id != game_id
        _finish_pending_game(
            binder_id,
            pending,
            catalog_id=game_id,
            override_action="replace" if needs_override else None,
            reason=(
                "Catalog identity selected while resolving the imported listing."
                if needs_override
                else None
            ),
        )
        print(f"Added {game_id} to {binder_id}.")
        return 0, True


def _add_pending_games(binder_id):
    while True:
        try:
            with _claim_next_pending_game(binder_id) as pending:
                if pending is None:
                    remaining = len(load_binder(binder_id).pending_games)
                    if remaining:
                        print(
                            f"No unclaimed work is available; {remaining} pending "
                            "game(s) are active in other terminals."
                        )
                    else:
                        print(f"No pending games remain in {binder_id}.")
                    return 0
                result, completed = _process_pending_game(binder_id, pending)
        except (BinderError, OSError) as error:
            print(f"ERROR: could not process pending binder game: {error}", file=sys.stderr)
            return 1
        if result:
            return result
        if not completed:
            return 0


def interactive_add_game(description="", binder_id=None):
    if binder_id is not None:
        if description.strip():
            print("ERROR: use either a game description or --binder, not both.", file=sys.stderr)
            return 2
        return _add_pending_games(binder_id)
    description, game_id = _request_new_identity(description)
    if not game_id:
        return 2
    with _claim_add_game(game_id) as claimed:
        if not claimed:
            print(
                f"Another game workflow is already working on {game_id}; "
                "this invocation made no changes."
            )
            return 0
        return _resume_add_game(description, game_id)


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
        if not validate_game_contexts(candidate, game_id):
            print("Candidate discarded because one or more render contexts failed.")
            return False
        if not ask_yes_no("Replace the current content with this candidate?"):
            print("Candidate discarded; the original YAML is unchanged.")
            return False
        candidate.replace(content_path)
    print(f"Updated {content_path.relative_to(ROOT)}")
    return True


def interactive_update_game(game=""):
    game_id = _request_game_id(game)
    if not game_id:
        return 2
    print(f"\nUpdating catalog game {_game_name(game_id)}.")
    print("  1. Refresh researched content")
    print("  2. Replace the playfield image")
    print("  3. Redo shot labels")
    print("  4. Validate and build affected binder packets")
    try:
        actions = input("Choose steps (comma-separated) [4]: ").strip() or "4"
    except EOFError:
        actions = "4"
    requested = {part.strip() for part in actions.split(",") if part.strip()}
    if not requested <= {"1", "2", "3", "4"}:
        print("ERROR: choose one or more numbers from 1 through 4.", file=sys.stderr)
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
    content_path = CONTENT / f"{game_id}.yaml"
    if not validate_game_contexts(content_path, game_id):
        return 1
    try:
        affected = binders_containing(game_id)
    except BinderError as error:
        print(f"ERROR: could not validate affected binders: {error}", file=sys.stderr)
        return 1
    printed = [binder for binder in affected if binder.status == "printed"]
    print(
        f"Validated the catalog game against {len(affected)} binder(s); "
        f"{len(printed)} printed binder(s) need replacement packets."
    )
    if "4" not in requested or not printed:
        return 0
    if not ask_yes_no(f"Build {len(printed)} four-page update packet(s)?"):
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
        packets = [
            build_print_packet(game_id, "update", binder, black_and_white)
            for binder in printed
        ]
    except (BuildInputError, OSError, ValueError) as error:
        print(f"ERROR: could not build update packet: {error}", file=sys.stderr)
        return 1
    for packet in packets:
        print(f"Print {packet.relative_to(ROOT)} double-sided, flipping on the long edge.")
    return 0
