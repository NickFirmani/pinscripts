"""Catalog/binder validation, PDF rendering, and replacement packets."""

import sys
import tempfile
from pathlib import Path

from .binder import BinderError, binders_containing, load_binder, load_binders, neighboring_entries
from .catalog import CatalogError, content_paths
from .content import load_yaml, schema_validator, validate_content
from .paths import CONTENT, OUTPUT
from .pdf import merge_pdfs, merge_print_packet, render_game
from .shot_labels import ShotLabelError, load_shot_labels


class BuildInputError(ValueError):
    pass


def validate_all(paths):
    validator = schema_validator()
    valid = True
    for path in paths:
        errors = validate_content(path, validator)
        data = None
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
                game_id = data.get("id", path.stem) if isinstance(data, dict) else path.stem
                errors.append(
                    f"shot labels: {error}; run make shot-labels GAME=\"{game_id}\""
                )
            except (OSError, AttributeError) as error:
                errors.append(str(error))
        if errors:
            valid = False
            print(f"ERROR: validation failed: {path}", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        else:
            print(f"Validated {path}")
    return valid


def validate_project():
    try:
        paths = content_paths()
        binders = load_binders()
    except (CatalogError, BinderError) as error:
        print(f"ERROR: validation failed: {error}", file=sys.stderr)
        return 1
    if not validate_all(paths):
        return 1
    print(f"Validated {len(paths)} catalog game(s) and {len(binders)} binder(s).")
    return 0


def validate_game_contexts(content_path, game_id):
    """Validate layout for the catalog and every binder-specific rendering."""
    if not validate_all([content_path]):
        return False
    try:
        binders = binders_containing(game_id)
    except BinderError as error:
        print(f"ERROR: invalid affected binder: {error}", file=sys.stderr)
        return False
    OUTPUT.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix="validate-game-", dir=OUTPUT) as directory:
            temporary = Path(directory)
            render_game(content_path, temporary / "catalog.pdf", venue_notes=())
            for binder in binders:
                entry = binder.entry(game_id, include_removed=False)
                render_game(
                    content_path,
                    temporary / f"{binder.binder_id}.pdf",
                    page_labels=entry.pages,
                    venue_notes=entry.venue_notes,
                )
    except (OSError, ValueError) as error:
        print(f"ERROR: {game_id} failed a rendered binder context: {error}", file=sys.stderr)
        return False
    print(f"Validated {game_id} in the catalog and {len(binders)} binder context(s).")
    return True


def render(paths, black_and_white=False, page_labels=None, venue_notes=None):
    output_suffix = "-bw" if black_and_white else ""
    for index, path in enumerate(paths):
        options = {}
        if page_labels is not None:
            options["page_labels"] = page_labels[path.stem]
        else:
            options["page_number_start"] = (index * 2) + 2
        if venue_notes is not None:
            options["venue_notes"] = venue_notes.get(path.stem, ())
        render_game(
            path,
            OUTPUT / f"{path.stem}{output_suffix}.pdf",
            black_and_white,
            **options,
        )


def _build_collection(
    paths,
    output_path,
    black_and_white=False,
    page_labels=None,
    venue_notes=None,
    title=None,
    source_credit=None,
):
    if not validate_all(paths):
        return 1
    render(paths, black_and_white, page_labels, venue_notes)
    suffix = "-bw" if black_and_white else ""
    pdfs = [OUTPUT / f"{path.stem}{suffix}.pdf" for path in paths]
    merge_pdfs(pdfs, output_path, title, source_credit)
    return 0


def build_game(game_id, black_and_white=False, binder_id=None):
    path = CONTENT / f"{game_id}.yaml"
    if not path.exists():
        raise BuildInputError(f"no catalog content file: {path}")
    options = {}
    if binder_id:
        try:
            binder = load_binder(binder_id)
            entry = binder.entry(game_id, include_removed=False)
        except BinderError as error:
            raise BuildInputError(str(error)) from error
        options = {"page_labels": entry.pages, "venue_notes": entry.venue_notes}
    if not validate_all([path]):
        return 1
    suffix = "-bw" if black_and_white else ""
    render_game(path, OUTPUT / f"{game_id}{suffix}.pdf", black_and_white, **options)
    return 0


def build_catalog(black_and_white=False):
    try:
        paths = content_paths()
    except CatalogError as error:
        print(f"ERROR: invalid catalog: {error}", file=sys.stderr)
        return 1
    suffix = "-bw" if black_and_white else ""
    return _build_collection(
        paths,
        OUTPUT / f"catalog{suffix}.pdf",
        black_and_white,
        title="Master Catalog",
    )


def build_binder(binder_id, black_and_white=False):
    try:
        binder = load_binder(binder_id)
    except BinderError as error:
        print(f"ERROR: invalid binder manifest: {error}", file=sys.stderr)
        return 1
    entries = binder.active_games
    paths = [CONTENT / f"{entry.game_id}.yaml" for entry in entries]
    labels = {entry.game_id: entry.pages for entry in entries}
    notes = {entry.game_id: entry.venue_notes for entry in entries}
    suffix = "-bw" if black_and_white else ""
    output_path = OUTPUT / "binders" / f"{binder.binder_id}{suffix}.pdf"
    source_credit = (
        "Lineup reference: Pinball Map (advisory; manually curated manifest)"
        if binder.source.url
        else None
    )
    return _build_collection(
        paths,
        output_path,
        black_and_white,
        labels,
        notes,
        binder.title,
        source_credit,
    )


def build_print_packet(game_id, operation, binder_id_or_object, black_and_white=False):
    if operation not in {"add", "update"}:
        raise BuildInputError("print-packet operation must be add or update")
    try:
        binder = (
            binder_id_or_object
            if hasattr(binder_id_or_object, "active_games")
            else load_binder(binder_id_or_object)
        )
        target = binder.entry(game_id, include_removed=False)
        previous, following = neighboring_entries(binder, game_id)
    except BinderError as error:
        raise BuildInputError(str(error)) from error

    entries = [entry for entry in (previous, target, following) if entry is not None]
    paths = [CONTENT / f"{entry.game_id}.yaml" for entry in entries]
    if not validate_all(paths):
        raise BuildInputError("print-packet content failed validation")

    suffix = "-bw" if black_and_white else ""
    packet_path = OUTPUT / "print" / binder.binder_id / f"{operation}-{game_id}{suffix}.pdf"
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
                venue_notes=entry.venue_notes,
            )
            rendered[entry.game_id] = rendered_path
        merge_print_packet(
            rendered[game_id],
            packet_path,
            rendered[previous.game_id] if previous else None,
            rendered[following.game_id] if following else None,
        )
    return packet_path


def build_update_packets(game_id, black_and_white=False):
    try:
        binders = [binder for binder in binders_containing(game_id) if binder.status == "printed"]
    except BinderError as error:
        raise BuildInputError(str(error)) from error
    return [
        build_print_packet(game_id, "update", binder, black_and_white)
        for binder in binders
    ]
