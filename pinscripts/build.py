"""Validation, PDF rendering, binder assembly, and print-packet workflows."""

import sys
import tempfile
from pathlib import Path

from .pdf import merge_pdfs, merge_print_packet, render_game

from .content import (
    load_yaml,
    schema_validator,
    validate_content,
)
from .manual import ManualError, load_manual, neighboring_entries
from .paths import CONTENT, OUTPUT
from .shot_labels import ShotLabelError, load_shot_labels


class BuildInputError(ValueError):
    pass


def validate_all(paths):
    validator = schema_validator()
    valid = True

    for path in paths:
        errors = validate_content(path, validator)
        if not errors:
            try:
                data = load_yaml(path)
                if data.get("id") != path.stem:
                    errors.append(
                        f"$.id: expected {path.stem!r} to match the filename, "
                        f"got {data.get('id')!r}"
                    )
                else:
                    load_shot_labels(data)
            except ShotLabelError as error:
                errors.append(
                    f"shot labels: {error}; run "
                    f"make shot-labels GAME=\"{data.get('id', path.stem)}\""
                )
        if errors:
            valid = False
            print(f"ERROR: validation failed: {path}", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        else:
            print(f"Validated {path}")

    return valid


def render(paths, black_and_white=False, binder=False, page_labels=None):
    output_suffix = "-bw" if black_and_white else ""
    for index, path in enumerate(paths):
        footer_options = {}
        if page_labels is not None:
            footer_options["page_labels"] = page_labels[path.stem]
        elif binder:
            footer_options["page_number_start"] = (index * 2) + 2
        render_game(
            path,
            OUTPUT / f"{path.stem}{output_suffix}.pdf",
            black_and_white,
            **footer_options,
        )


def build_paths(paths, black_and_white=False, binder=False, page_labels=None):
    if not validate_all(paths):
        return 1

    render(paths, black_and_white, binder, page_labels)
    if binder:
        output_suffix = "-bw" if black_and_white else ""
        pdfs = [OUTPUT / f"{path.stem}{output_suffix}.pdf" for path in paths]
        merge_pdfs(pdfs, OUTPUT / f"binder{output_suffix}.pdf")
    return 0


def build_game(game_id, black_and_white=False):
    path = CONTENT / f"{game_id}.yaml"
    if not path.exists():
        raise BuildInputError(f"no content file: {path}")
    return build_paths([path], black_and_white)


def build_all(black_and_white=False):
    try:
        manual = load_manual()
    except ManualError as error:
        print(f"ERROR: invalid printed-manual manifest: {error}", file=sys.stderr)
        return 1
    paths = [CONTENT / f"{entry.game_id}.yaml" for entry in manual.games]
    labels = {entry.game_id: entry.pages for entry in manual.games}
    return build_paths(paths, black_and_white, binder=True, page_labels=labels)


def build_print_packet(game_id, operation, manual=None, black_and_white=False):
    """Render a game and one neighboring leaf on each side as a four-page PDF."""
    if operation not in {"add", "update"}:
        raise BuildInputError("print-packet operation must be add or update")
    if manual is None:
        try:
            manual = load_manual()
        except ManualError as error:
            raise BuildInputError(str(error)) from error
    try:
        target = manual.entry(game_id)
        previous, following = neighboring_entries(manual, game_id)
    except ManualError as error:
        raise BuildInputError(str(error)) from error

    entries = [entry for entry in (previous, target, following) if entry is not None]
    paths = [CONTENT / f"{entry.game_id}.yaml" for entry in entries]
    if not validate_all(paths):
        raise BuildInputError("print-packet content failed validation")

    output_suffix = "-bw" if black_and_white else ""
    packet_path = OUTPUT / "print" / f"{operation}-{game_id}{output_suffix}.pdf"
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="print-packet-", dir=OUTPUT) as directory:
        temporary = Path(directory)
        rendered = {}
        for entry in entries:
            path = CONTENT / f"{entry.game_id}.yaml"
            rendered_path = temporary / f"{entry.game_id}.pdf"
            render_game(
                path,
                rendered_path,
                black_and_white,
                page_labels=entry.pages,
            )
            rendered[entry.game_id] = rendered_path
        merge_print_packet(
            rendered[game_id],
            packet_path,
            rendered[previous.game_id] if previous else None,
            rendered[following.game_id] if following else None,
        )
    return packet_path
