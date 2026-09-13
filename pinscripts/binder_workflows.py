"""Interactive creation, synchronization, and maintenance of binder manifests."""

from dataclasses import replace
from pathlib import Path
import sys

from .binder import (
    BinderError,
    BinderSource,
    PendingGame,
    add_game,
    binder_path,
    create_binder,
    load_binder,
    mark_manually_curated,
    mark_printed,
    remove_game,
    replace_entry,
    write_binder,
)
from .catalog import CatalogError, catalog_by_id, match_imported_game, resolve_game
from .game_workflows import ask_yes_no
from .pinball_map import (
    ImportedLocation,
    PinballMapError,
    fetch_location,
    pasted_location,
)


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


def _pending_game(imported):
    return PendingGame(imported.name, imported.manufacturer, imported.year)


def classify_imported(imported_location, binder=None):
    """Resolve imports using saved overrides, exact matches, or the pending queue."""
    catalog = catalog_by_id()
    resolved = []
    pending = []
    ignored = []
    overrides = {
        override.imported.key: override
        for override in (binder.source_overrides if binder is not None else ())
    }
    for imported in imported_location.games:
        candidate = _pending_game(imported)
        override = overrides.get(candidate.key)
        if override is not None:
            if override.action == "ignore":
                ignored.append(candidate)
            else:
                resolved.append((candidate, override.catalog_id, True))
            continue
        match = match_imported_game(imported, catalog)
        if match is None:
            pending.append(candidate)
        else:
            resolved.append((candidate, match.game_id, False))
    return resolved, pending, ignored


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
            resolved, pending_games, _ignored = classify_imported(imported)
            game_ids = list(dict.fromkeys(game_id for _item, game_id, _override in resolved))
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
        binder = create_binder(
            binder_id,
            resolved_title,
            game_ids,
            source,
            pending_games=pending_games if not games_file else (),
        )
        destination = write_binder(binder)
    except (BinderError, CatalogError, PinballMapError, OSError) as error:
        print(f"ERROR: could not create binder: {error}", file=sys.stderr)
        return 1
    print(
        f"Created draft binder {destination} with {len(binder.games)} ready game(s) "
        f"and {len(binder.pending_games)} pending game(s)."
    )
    return 0


def sync_binder_interactive(binder_id, *, pinball_map=None, paste=False):
    try:
        binder = load_binder(binder_id)
        source_value = None if paste else (pinball_map or binder.source.location_id)
        imported = _load_import(source_value, paste, binder.title)
        resolved, unresolved, ignored = classify_imported(imported, binder)
        imported_ids = [game_id for _item, game_id, _override in resolved]
        current = {entry.game_id for entry in binder.active_games}
        imported_set = set(imported_ids)
        additions = [item for item in resolved if item[1] not in current]
        only_in_binder = [entry.game_id for entry in binder.active_games if entry.game_id not in imported_set]
        print(f"\nSync preview for {binder.title}:")
        print(f"  {len(current & imported_set)} matched")
        print(f"  {len(additions)} only on the imported listing")
        print(f"  {len(only_in_binder)} only in the binder (kept)")
        print(f"  {len(unresolved)} unresolved imported game(s) queued")
        print(f"  {len(ignored)} ignored by saved overrides")
        catalog = catalog_by_id()
        updated = binder
        pending_by_key = {pending.key: pending for pending in binder.pending_games}
        ignored_keys = {pending.key for pending in ignored}
        pending_by_key = {
            key: pending for key, pending in pending_by_key.items() if key not in ignored_keys
        }
        for pending in unresolved:
            pending_by_key.setdefault(pending.key, pending)
        for pending, game_id, overridden in additions:
            if pending.key in pending_by_key and not overridden:
                continue
            if ask_yes_no(f"Add {catalog[game_id].name} to the binder?", default=False):
                updated = add_game(updated, game_id, catalog)
                pending_by_key.pop(pending.key, None)
        for pending, game_id, _overridden in resolved:
            if game_id in current:
                pending_by_key.pop(pending.key, None)
        updated_source = replace(
            updated.source,
            location_id=imported.location_id or updated.source.location_id,
            url=imported.url or updated.source.url,
            retrieved_at=imported.retrieved_at,
        )
        updated = replace(
            updated,
            source=updated_source,
            pending_games=tuple(
                sorted(pending_by_key.values(), key=lambda item: item.description.casefold())
            ),
        )
        write_binder(updated)
    except (BinderError, CatalogError, PinballMapError, OSError) as error:
        print(f"ERROR: could not sync binder: {error}", file=sys.stderr)
        return 1
    print(
        "Saved binder. Games absent from the advisory listing were not removed; "
        f"{len(updated.pending_games)} game(s) remain pending."
    )
    return 0


def add_binder_game(binder_id, game_query):
    try:
        binder = load_binder(binder_id)
        game = resolve_game(game_query)
        if game is None:
            raise BinderError(f"no unique catalog game matched {game_query!r}")
        updated = mark_manually_curated(
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
        updated = mark_manually_curated(
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


def show_binder_status(binder_id):
    try:
        binder = load_binder(binder_id)
    except (BinderError, OSError) as error:
        print(f"ERROR: could not read binder status: {error}", file=sys.stderr)
        return 1
    ignored = sum(
        override.action == "ignore" for override in binder.source_overrides
    )
    corrected = sum(
        override.action == "replace" for override in binder.source_overrides
    )
    print(f"{binder.title} ({binder.binder_id})")
    print(f"  state: {binder.status}")
    print(f"  ready games: {len(binder.active_games)}")
    print(f"  pending games: {len(binder.pending_games)}")
    print(f"  ignored imports: {ignored}")
    print(f"  corrected imports: {corrected}")
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
        updated = mark_manually_curated(
            replace_entry(binder, replace(entry, venue_notes=tuple(notes)))
        )
        write_binder(updated)
    except (BinderError, CatalogError, OSError) as error:
        print(f"ERROR: could not edit venue notes: {error}", file=sys.stderr)
        return 1
    print(f"Saved {len(notes)} venue note(s) for {game.name} in {binder.title}.")
    return 0
