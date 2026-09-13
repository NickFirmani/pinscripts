"""Manifests for printable and already-printed physical binders."""

from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR
from pathlib import Path
import re
import tempfile

import yaml

from .content import PIN_ID_PATTERN, normalized_game_id
from .locks import claim_lock
from .paths import BINDERS, CONTENT


PAGE_LABEL_PATTERN = re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?")
BINDER_ID_PATTERN = PIN_ID_PATTERN
SOURCE_KINDS = {"manual", "pinball-map"}
BINDER_STATUSES = {"draft", "printed"}
OVERRIDE_ACTIONS = {"ignore", "replace"}
MANUAL_SOURCE_NOTE = (
    "Manually curated; any retained Pinball Map URL is an advisory reference only."
)


class BinderError(ValueError):
    """Raised when a binder manifest is invalid."""


@dataclass(frozen=True)
class BinderSource:
    kind: str
    location_id: str | None = None
    url: str | None = None
    retrieved_at: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class BinderEntry:
    game_id: str
    pages: tuple[str, str]
    present: bool = True
    venue_notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PendingGame:
    name: str
    manufacturer: str
    year: int

    @property
    def description(self):
        return f"{self.name} ({self.manufacturer}, {self.year})"

    @property
    def key(self):
        return "|".join(
            (
                normalized_game_id(self.name),
                normalized_game_id(self.manufacturer),
                str(self.year),
            )
        )


@dataclass(frozen=True)
class SourceOverride:
    imported: PendingGame
    action: str
    catalog_id: str | None = None
    reason: str | None = None


@dataclass(frozen=True)
class Binder:
    version: int
    binder_id: str
    title: str
    status: str
    printed_at: str | None
    source: BinderSource
    games: tuple[BinderEntry, ...]
    pending_games: tuple[PendingGame, ...] = ()
    source_overrides: tuple[SourceOverride, ...] = ()

    def index(self, game_id, include_removed=True):
        for index, entry in enumerate(self.games):
            if entry.game_id == game_id and (include_removed or entry.present):
                return index
        raise BinderError(f"game is not in binder {self.binder_id}: {game_id}")

    def entry(self, game_id, include_removed=True):
        return self.games[self.index(game_id, include_removed)]

    @property
    def active_games(self):
        return tuple(entry for entry in self.games if entry.present)


def binder_path(binder_id, binders_directory=BINDERS):
    return binders_directory / f"{binder_id}.yaml"


def _page_value(label):
    if not isinstance(label, str) or PAGE_LABEL_PATTERN.fullmatch(label) is None:
        raise BinderError(
            f"invalid page label {label!r}; use a positive integer or decimal string"
        )
    try:
        value = Decimal(label)
    except InvalidOperation as error:
        raise BinderError(f"invalid page label: {label!r}") from error
    if value <= 0:
        raise BinderError(f"page labels must be positive: {label!r}")
    return value


def _date_or_none(value, field):
    if value is None:
        return None
    if not isinstance(value, str):
        raise BinderError(f"{field} must be a YYYY-MM-DD string or null")
    try:
        date.fromisoformat(value)
    except ValueError as error:
        raise BinderError(f"{field} must be a valid YYYY-MM-DD date") from error
    return value


def _pending_from_data(data, field):
    if not isinstance(data, dict) or set(data) != {"name", "manufacturer", "year"}:
        raise BinderError(f"{field} must contain exactly name, manufacturer, and year")
    name = data["name"]
    manufacturer = data["manufacturer"]
    year = data["year"]
    if not isinstance(name, str) or not name.strip():
        raise BinderError(f"{field}.name must be a non-empty string")
    if not isinstance(manufacturer, str) or not manufacturer.strip():
        raise BinderError(f"{field}.manufacturer must be a non-empty string")
    if not isinstance(year, int) or isinstance(year, bool) or not 1930 <= year <= 2100:
        raise BinderError(f"{field}.year must be an integer from 1930 through 2100")
    return PendingGame(name.strip(), manufacturer.strip(), year)


def _pending_data(pending):
    return {
        "name": pending.name,
        "manufacturer": pending.manufacturer,
        "year": pending.year,
    }


def binder_from_data(data, *, path=None, content_directory=CONTENT, require_content=True):
    if not isinstance(data, dict):
        raise BinderError("binder manifest must contain a mapping")
    expected = {
        "version",
        "id",
        "title",
        "status",
        "printed_at",
        "source",
        "pending_games",
        "source_overrides",
        "games",
    }
    if set(data) != expected:
        missing = sorted(expected - set(data))
        extra = sorted(set(data) - expected)
        details = []
        if missing:
            details.append("missing keys: " + ", ".join(missing))
        if extra:
            details.append("unknown keys: " + ", ".join(extra))
        raise BinderError("; ".join(details))
    if data["version"] != 2:
        raise BinderError("binder version must be 2")
    binder_id = data["id"]
    if not isinstance(binder_id, str) or BINDER_ID_PATTERN.fullmatch(binder_id) is None:
        raise BinderError(f"invalid binder id: {binder_id!r}")
    if path is not None and Path(path).stem != binder_id:
        raise BinderError(
            f"binder id {binder_id!r} must match filename {Path(path).stem!r}"
        )
    title = data["title"]
    if not isinstance(title, str) or not title.strip():
        raise BinderError("binder title must be a non-empty string")
    status = data["status"]
    if status not in BINDER_STATUSES:
        raise BinderError("binder status must be draft or printed")
    printed_at = _date_or_none(data["printed_at"], "printed_at")
    if status == "draft" and printed_at is not None:
        raise BinderError("a draft binder must have printed_at: null")

    source_data = data["source"]
    source_keys = {"kind", "location_id", "url", "retrieved_at", "notes"}
    if not isinstance(source_data, dict) or set(source_data) != source_keys:
        raise BinderError("source must contain exactly kind, location_id, url, retrieved_at, and notes")
    kind = source_data["kind"]
    if kind not in SOURCE_KINDS:
        raise BinderError("source kind must be manual or pinball-map")
    location_id = source_data["location_id"]
    if location_id is not None and (
        not isinstance(location_id, str) or not location_id.isdigit()
    ):
        raise BinderError("source.location_id must be a numeric string or null")
    url = source_data["url"]
    if url is not None and (not isinstance(url, str) or not url.startswith("https://")):
        raise BinderError("source.url must be an https URL or null")
    retrieved_at = _date_or_none(source_data["retrieved_at"], "source.retrieved_at")
    notes = source_data["notes"]
    if notes is not None and (not isinstance(notes, str) or len(notes) > 500):
        raise BinderError("source.notes must be a string of at most 500 characters or null")
    if kind == "pinball-map" and not location_id:
        raise BinderError("a pinball-map source requires location_id")
    source = BinderSource(kind, location_id, url, retrieved_at, notes)

    if not isinstance(data["pending_games"], list):
        raise BinderError("pending_games must be a list")
    pending_games = tuple(
        _pending_from_data(item, f"pending_games entry {position}")
        for position, item in enumerate(data["pending_games"], start=1)
    )
    pending_keys = [pending.key for pending in pending_games]
    if len(pending_keys) != len(set(pending_keys)):
        raise BinderError("pending_games contains a duplicate imported game")

    if not isinstance(data["source_overrides"], list):
        raise BinderError("source_overrides must be a list")
    source_overrides = []
    override_keys = set()
    for position, item in enumerate(data["source_overrides"], start=1):
        field = f"source_overrides entry {position}"
        if not isinstance(item, dict) or set(item) != {
            "imported", "action", "catalog_id", "reason"
        }:
            raise BinderError(
                f"{field} must contain exactly imported, action, catalog_id, and reason"
            )
        imported = _pending_from_data(item["imported"], f"{field}.imported")
        if imported.key in override_keys:
            raise BinderError("source_overrides contains a duplicate imported game")
        override_keys.add(imported.key)
        action = item["action"]
        if action not in OVERRIDE_ACTIONS:
            raise BinderError(f"{field}.action must be ignore or replace")
        catalog_id = item["catalog_id"]
        if action == "replace":
            if not isinstance(catalog_id, str) or PIN_ID_PATTERN.fullmatch(catalog_id) is None:
                raise BinderError(f"{field}.catalog_id must be a game ID for replace")
            if require_content and not (content_directory / f"{catalog_id}.yaml").is_file():
                raise BinderError(f"source override has no catalog content: {catalog_id}")
        elif catalog_id is not None:
            raise BinderError(f"{field}.catalog_id must be null for ignore")
        reason = item["reason"]
        if reason is not None and (
            not isinstance(reason, str) or not reason.strip() or len(reason) > 300
        ):
            raise BinderError(f"{field}.reason must be null or 1-300 characters")
        source_overrides.append(SourceOverride(imported, action, catalog_id, reason))
    overlap = set(pending_keys) & override_keys
    if overlap:
        raise BinderError("an imported game cannot be both pending and overridden")

    if not isinstance(data["games"], list):
        raise BinderError("games must be a list")
    entries = []
    seen_ids = set()
    seen_pages = set()
    previous_page = None
    for position, item in enumerate(data["games"], start=1):
        if not isinstance(item, dict) or set(item) != {
            "id", "pages", "present", "venue_notes"
        }:
            raise BinderError(
                f"games entry {position} must contain exactly id, pages, present, and venue_notes"
            )
        game_id = item["id"]
        if not isinstance(game_id, str) or PIN_ID_PATTERN.fullmatch(game_id) is None:
            raise BinderError(f"games entry {position} has an invalid id: {game_id!r}")
        if game_id in seen_ids:
            raise BinderError(f"duplicate game id in binder: {game_id}")
        seen_ids.add(game_id)
        if require_content and not (content_directory / f"{game_id}.yaml").is_file():
            raise BinderError(f"binder game has no catalog content: {game_id}")
        pages = item["pages"]
        if not isinstance(pages, list) or len(pages) != 2:
            raise BinderError(f"{game_id} must have exactly two page labels")
        page_values = [_page_value(label) for label in pages]
        if page_values[0] >= page_values[1]:
            raise BinderError(f"page labels for {game_id} must be increasing")
        if any(label in seen_pages for label in pages):
            raise BinderError(f"duplicate page label in binder: {pages}")
        seen_pages.update(pages)
        if previous_page is not None and page_values[0] <= previous_page:
            raise BinderError(
                f"page labels are not increasing before {game_id}: {pages[0]}"
            )
        previous_page = page_values[1]
        if not isinstance(item["present"], bool):
            raise BinderError(f"{game_id}.present must be true or false")
        venue_notes = item["venue_notes"]
        if (
            not isinstance(venue_notes, list)
            or len(venue_notes) > 10
            or any(not isinstance(note, str) or not note or len(note) > 300 for note in venue_notes)
        ):
            raise BinderError(f"{game_id}.venue_notes must contain up to 10 non-empty strings")
        entries.append(
            BinderEntry(game_id, (pages[0], pages[1]), item["present"], tuple(venue_notes))
        )
    return Binder(
        2,
        binder_id,
        title,
        status,
        printed_at,
        source,
        tuple(entries),
        pending_games,
        tuple(source_overrides),
    )


def binder_data(binder):
    return {
        "version": binder.version,
        "id": binder.binder_id,
        "title": binder.title,
        "status": binder.status,
        "printed_at": binder.printed_at,
        "source": {
            "kind": binder.source.kind,
            "location_id": binder.source.location_id,
            "url": binder.source.url,
            "retrieved_at": binder.source.retrieved_at,
            "notes": binder.source.notes,
        },
        "pending_games": [_pending_data(pending) for pending in binder.pending_games],
        "source_overrides": [
            {
                "imported": _pending_data(override.imported),
                "action": override.action,
                "catalog_id": override.catalog_id,
                "reason": override.reason,
            }
            for override in binder.source_overrides
        ],
        "games": [
            {
                "id": entry.game_id,
                "pages": list(entry.pages),
                "present": entry.present,
                "venue_notes": list(entry.venue_notes),
            }
            for entry in binder.games
        ],
    }


def load_binder(binder_id_or_path, *, binders_directory=BINDERS, content_directory=CONTENT, require_content=True):
    supplied = Path(binder_id_or_path)
    path = supplied if supplied.suffix == ".yaml" or supplied.parent != Path(".") else binder_path(str(binder_id_or_path), binders_directory)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise BinderError(f"could not read binder manifest {path}: {error}") from error
    except yaml.YAMLError as error:
        raise BinderError(f"invalid YAML in {path}: {error}") from error
    return binder_from_data(data, path=path, content_directory=content_directory, require_content=require_content)


def write_binder(binder, *, path=None, binders_directory=BINDERS):
    destination = Path(path) if path is not None else binder_path(binder.binder_id, binders_directory)
    binder_from_data(binder_data(binder), path=destination, require_content=False)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", prefix=f".{destination.name}-", suffix=".tmp",
        dir=destination.parent, delete=False,
    ) as temporary:
        yaml.safe_dump(binder_data(binder), temporary, sort_keys=False, allow_unicode=True)
        temporary_path = Path(temporary.name)
    temporary_path.replace(destination)
    return destination


def mutate_binder(
    binder_id,
    mutator,
    *,
    binders_directory=BINDERS,
    content_directory=CONTENT,
    lock_directory=None,
):
    """Reload, mutate, and atomically write one binder under a short lock."""
    with claim_lock(
        f"binder-{binder_id}",
        blocking=True,
        lock_directory=lock_directory,
    ) as claimed:
        if not claimed:  # Blocking acquisition always claims; defensive only.
            raise BinderError(f"could not lock binder: {binder_id}")
        binder = load_binder(
            binder_id,
            binders_directory=binders_directory,
            content_directory=content_directory,
        )
        updated = mutator(binder)
        write_binder(
            updated,
            path=binder_path(binder_id, binders_directory),
            binders_directory=binders_directory,
        )
        return updated


def mark_manually_curated(binder):
    notes = binder.source.notes
    if notes is None or "manually" not in notes.casefold():
        notes = MANUAL_SOURCE_NOTE
    return replace(binder, source=replace(binder.source, kind="manual", notes=notes))


def load_binders(binders_directory=BINDERS, content_directory=CONTENT):
    return [
        load_binder(path, binders_directory=binders_directory, content_directory=content_directory)
        for path in sorted(binders_directory.glob("*.yaml"))
    ] if binders_directory.is_dir() else []


def binders_containing(game_id, binders_directory=BINDERS, content_directory=CONTENT):
    return [
        binder for binder in load_binders(binders_directory, content_directory)
        if any(entry.game_id == game_id and entry.present for entry in binder.games)
    ]


def _format_tick(tick, decimal_places):
    if decimal_places == 0:
        return str(tick)
    digits = str(tick).zfill(decimal_places + 1)
    return f"{digits[:-decimal_places]}.{digits[-decimal_places:]}"


def allocate_page_labels(left_label, right_label=None):
    left = _page_value(left_label)
    right = _page_value(right_label) if right_label is not None else None
    if right is None:
        right = left.to_integral_value(rounding=ROUND_CEILING)
        if right <= left:
            right += 1
    if left >= right:
        raise BinderError(f"cannot allocate pages between {left_label} and {right_label}")
    for decimal_places in range(1, 13):
        scale = Decimal(10) ** decimal_places
        first_tick = int((left * scale).to_integral_value(rounding=ROUND_FLOOR)) + 1
        last_tick = int((right * scale).to_integral_value(rounding=ROUND_CEILING)) - 1
        if last_tick - first_tick + 1 >= 2:
            return (
                _format_tick(first_tick, decimal_places),
                _format_tick(first_tick + 1, decimal_places),
            )
    raise BinderError("page labels are too densely allocated; manual intervention is required")


def create_binder(
    binder_id,
    title,
    game_ids,
    source=None,
    *,
    pending_games=(),
    source_overrides=(),
):
    source = source or BinderSource("manual")
    entries = tuple(
        BinderEntry(game_id, (str(index * 2 + 2), str(index * 2 + 3)))
        for index, game_id in enumerate(game_ids)
    )
    return Binder(
        2,
        binder_id,
        title,
        "draft",
        None,
        source,
        entries,
        tuple(pending_games),
        tuple(source_overrides),
    )


def _entry_sort_key(entry, catalog):
    game = catalog.get(entry.game_id)
    return ((game.name if game else entry.game_id).casefold(), entry.game_id)


def renumber_draft(binder, catalog):
    if binder.status != "draft":
        raise BinderError("only draft binders may be renumbered")
    active = sorted(binder.active_games, key=lambda entry: _entry_sort_key(entry, catalog))
    entries = tuple(
        replace(entry, pages=(str(index * 2 + 2), str(index * 2 + 3)))
        for index, entry in enumerate(active)
    )
    return replace(binder, games=entries)


def add_game(binder, game_id, catalog, venue_notes=()):
    if any(entry.game_id == game_id for entry in binder.games):
        raise BinderError(f"game is already recorded in binder {binder.binder_id}: {game_id}")
    if game_id not in catalog:
        raise BinderError(f"game is not in the catalog: {game_id}")
    new_entry = BinderEntry(game_id, ("1", "2"), True, tuple(venue_notes))
    if binder.status == "draft":
        return renumber_draft(replace(binder, games=binder.games + (new_entry,)), catalog)

    entries = list(binder.games)
    key = _entry_sort_key(new_entry, catalog)
    index = next(
        (i for i, entry in enumerate(entries) if key < _entry_sort_key(entry, catalog)),
        len(entries),
    )
    left_label = entries[index - 1].pages[1] if index else "1"
    right_label = entries[index].pages[0] if index < len(entries) else None
    entries.insert(index, replace(new_entry, pages=allocate_page_labels(left_label, right_label)))
    return replace(binder, games=tuple(entries))


def remove_game(binder, game_id, catalog):
    entry = binder.entry(game_id)
    if binder.status == "printed":
        return replace_entry(binder, replace(entry, present=False))
    remaining = tuple(item for item in binder.games if item.game_id != game_id)
    return renumber_draft(replace(binder, games=remaining), catalog)


def mark_printed(binder, printed_at=None):
    if binder.pending_games:
        raise BinderError(
            f"cannot mark binder printed with {len(binder.pending_games)} pending game(s)"
        )
    return replace(binder, status="printed", printed_at=printed_at or date.today().isoformat())


def replace_entry(binder, updated_entry):
    entries = [updated_entry if entry.game_id == updated_entry.game_id else entry for entry in binder.games]
    return replace(binder, games=tuple(entries))


def neighboring_entries(binder, game_id):
    active = list(binder.active_games)
    index = next((i for i, entry in enumerate(active) if entry.game_id == game_id), None)
    if index is None:
        raise BinderError(f"active game is not in binder {binder.binder_id}: {game_id}")
    return (active[index - 1] if index else None, active[index + 1] if index + 1 < len(active) else None)
