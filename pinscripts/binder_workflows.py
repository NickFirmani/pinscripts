"""Interactive creation, synchronization, and maintenance of binder manifests."""

from dataclasses import replace
from pathlib import Path
import sys

from .binder import (
    BinderError,
    BinderSource,
    add_game,
    binder_path,
    create_binder,
    load_binder,
    mark_printed,
    remove_game,
    replace_entry,
    write_binder,
)
from .catalog import CatalogError, catalog_by_id, load_catalog, resolve_game
from .content import normalized_game_id
from .game_workflows import ask_yes_no, interactive_add_game
from .pinball_map import (
    ImportedLocation,
    PinballMapError,
    fetch_location,
    pasted_location,
)


MANUAL_SOURCE_NOTE = (
    "Manually curated; any retained Pinball Map URL is an advisory reference only."
)


def _mark_manually_curated(binder):
    notes = binder.source.notes
    if notes is None or "manually" not in notes.casefold():
        notes = MANUAL_SOURCE_NOTE
    return replace(binder, source=replace(binder.source, kind="manual", notes=notes))


def _manufacturer_key(value):
    value = normalized_game_id(value)
    aliases = {
        "stern-electronics": "stern",
        "stern-pinball": "stern",
        "bally-midway": "bally",
        "williams-electronic-games": "williams",
        "chicago-gaming-company": "chicago-gaming",
        "chicago-gaming-co": "chicago-gaming",
        "jersey-jack-pinball": "jersey-jack",
        "spooky-pinball": "spooky",
        "dutch-pinball": "dutch",
        "segasa-sonic": "segasa-sonic",
    }
    return aliases.get(value, value)


def match_imported_game(imported, catalog):
    """Return one conservative catalog match or None; never conflate editions."""
    name_key = normalized_game_id(imported.name)
    manufacturer_key = _manufacturer_key(imported.manufacturer)
    candidates = [
        game for game in catalog.values()
        if normalized_game_id(game.name) == name_key
        and game.year == imported.year
        and _manufacturer_key(game.manufacturer) == manufacturer_key
    ]
    if len(candidates) == 1:
        return candidates[0]
    return None


def _read_pasted_listing():
    print(
        "Paste one game per line as 'Game Name (Manufacturer, 2024)'. "
        "Finish with ::end."
    )
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "::end":
            break
        lines.append(line)
    return "\n".join(lines)


def _load_import(pinball_map=None, paste=False, title=None, fetcher=fetch_location):
    if pinball_map:
        return fetcher(pinball_map)
    if paste:
        return pasted_location(_read_pasted_listing(), title)
    raise BinderError("choose a Pinball Map location or pasted listing")


def _resolve_imported(imported_location, create_missing=True):
    catalog = catalog_by_id()
    resolved = []
    skipped = []
    for imported in imported_location.games:
        match = match_imported_game(imported, catalog)
        while match is None:
            print(f"\nNo exact catalog match: {imported.description}")
            try:
                answer = input(
                    "Enter a catalog game ID, [a]dd it, [s]kip it, or [q]uit: "
                ).strip()
            except EOFError:
                answer = "q"
            if answer.lower() in {"q", "quit"}:
                raise BinderError("binder import cancelled")
            if answer.lower() in {"s", "skip"}:
                skipped.append(imported)
                break
            if answer.lower() in {"a", "add"}:
                if not create_missing:
                    print("Adding catalog content is disabled for this operation.")
                    continue
                if interactive_add_game(imported.description):
                    print("Catalog add did not complete; the imported game remains unresolved.")
                    continue
                catalog = catalog_by_id()
                match = match_imported_game(imported, catalog)
                continue
            game = catalog.get(answer) or resolve_game(answer)
            if game is None:
                print(f"No unique catalog game matched {answer!r}.", file=sys.stderr)
                continue
            match = game
        if match is not None and match.game_id not in resolved:
            resolved.append(match.game_id)
    return resolved, skipped


def create_binder_interactive(
    binder_id,
    title=None,
    *,
    games_file=None,
    pinball_map=None,
    paste=False,
):
    destination = binder_path(binder_id)
    if destination.exists():
        print(f"ERROR: binder already exists: {destination}", file=sys.stderr)
        return 1
    try:
        if games_file:
            queries = [
                line.strip()
                for line in Path(games_file).read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            game_ids = []
            for query in queries:
                game = resolve_game(query)
                if game is None:
                    raise BinderError(f"no unique catalog game matched {query!r}")
                if game.game_id not in game_ids:
                    game_ids.append(game.game_id)
            source = BinderSource("manual", notes=f"Created from {Path(games_file).name}")
            resolved_title = title or binder_id.replace("-", " ").title()
        else:
            imported = _load_import(pinball_map, paste, title)
            game_ids, skipped = _resolve_imported(imported)
            if skipped:
                print(f"Skipped {len(skipped)} unresolved game(s).")
            resolved_title = title or imported.name or binder_id.replace("-", " ").title()
            source = BinderSource(
                "pinball-map" if imported.location_id else "manual",
                imported.location_id,
                imported.url,
                imported.retrieved_at,
                "Pinball Map is an advisory reference; this manifest is manually curated."
                if imported.location_id else None,
            )
        catalog = catalog_by_id()
        game_ids.sort(key=lambda game_id: (catalog[game_id].name.casefold(), game_id))
        binder = create_binder(binder_id, resolved_title, game_ids, source)
        destination = write_binder(binder)
    except (BinderError, CatalogError, PinballMapError, OSError) as error:
        print(f"ERROR: could not create binder: {error}", file=sys.stderr)
        return 1
    print(f"Created draft binder {destination} with {len(binder.games)} game(s).")
    return 0


def sync_binder_interactive(binder_id, *, pinball_map=None, paste=False):
    try:
        binder = load_binder(binder_id)
        source_value = None if paste else (pinball_map or binder.source.location_id)
        imported = _load_import(source_value, paste, binder.title)
        imported_ids, skipped = _resolve_imported(imported)
        current = {entry.game_id for entry in binder.active_games}
        imported_set = set(imported_ids)
        additions = [game_id for game_id in imported_ids if game_id not in current]
        only_in_binder = [entry.game_id for entry in binder.active_games if entry.game_id not in imported_set]
        print(f"\nSync preview for {binder.title}:")
        print(f"  {len(current & imported_set)} matched")
        print(f"  {len(additions)} only on the imported listing")
        print(f"  {len(only_in_binder)} only in the binder (kept)")
        print(f"  {len(skipped)} unresolved imported game(s)")
        catalog = catalog_by_id()
        updated = binder
        for game_id in additions:
            if ask_yes_no(f"Add {catalog[game_id].name} to the binder?", default=False):
                updated = add_game(updated, game_id, catalog)
        updated_source = replace(
            updated.source,
            location_id=imported.location_id or updated.source.location_id,
            url=imported.url or updated.source.url,
            retrieved_at=imported.retrieved_at,
        )
        updated = replace(updated, source=updated_source)
        write_binder(updated)
    except (BinderError, CatalogError, PinballMapError, OSError) as error:
        print(f"ERROR: could not sync binder: {error}", file=sys.stderr)
        return 1
    print("Saved binder. Games absent from the advisory listing were not removed.")
    return 0


def add_binder_game(binder_id, game_query):
    try:
        binder = load_binder(binder_id)
        game = resolve_game(game_query)
        if game is None:
            raise BinderError(f"no unique catalog game matched {game_query!r}")
        updated = _mark_manually_curated(
            add_game(binder, game.game_id, catalog_by_id())
        )
        write_binder(updated)
    except (BinderError, CatalogError, OSError) as error:
        print(f"ERROR: could not add binder game: {error}", file=sys.stderr)
        return 1
    print(f"Added {game.name} on pages {'-'.join(updated.entry(game.game_id).pages)}.")
    return 0


def remove_binder_game(binder_id, game_query):
    try:
        binder = load_binder(binder_id)
        game = resolve_game(game_query)
        if game is None:
            raise BinderError(f"no unique catalog game matched {game_query!r}")
        updated = _mark_manually_curated(
            remove_game(binder, game.game_id, catalog_by_id())
        )
        write_binder(updated)
    except (BinderError, CatalogError, OSError) as error:
        print(f"ERROR: could not remove binder game: {error}", file=sys.stderr)
        return 1
    action = "marked absent with its pages reserved" if binder.status == "printed" else "removed and renumbered"
    print(f"{game.name}: {action}.")
    return 0


def mark_binder_printed(binder_id, printed_at=None):
    try:
        binder = load_binder(binder_id)
        write_binder(mark_printed(binder, printed_at))
    except (BinderError, OSError) as error:
        print(f"ERROR: could not mark binder printed: {error}", file=sys.stderr)
        return 1
    print(f"Marked {binder_id} as printed.")
    return 0


def edit_venue_notes(binder_id, game_query):
    try:
        binder = load_binder(binder_id)
        game = resolve_game(game_query)
        if game is None:
            raise BinderError(f"no unique catalog game matched {game_query!r}")
        entry = binder.entry(game.game_id)
        print(f"Current venue notes for {game.name} in {binder.title}:")
        if entry.venue_notes:
            for index, note in enumerate(entry.venue_notes, start=1):
                print(f"  {index}. {note}")
        else:
            print("  (none)")
        print("Enter replacement notes one per line; finish with ::end. An empty list clears them.")
        notes = []
        while True:
            try:
                note = input().strip()
            except EOFError:
                break
            if note == "::end":
                break
            if note:
                notes.append(note)
        updated = _mark_manually_curated(
            replace_entry(binder, replace(entry, venue_notes=tuple(notes)))
        )
        write_binder(updated)
    except (BinderError, CatalogError, OSError) as error:
        print(f"ERROR: could not edit venue notes: {error}", file=sys.stderr)
        return 1
    print(f"Saved {len(notes)} venue note(s) for {game.name} in {binder.title}.")
    return 0
