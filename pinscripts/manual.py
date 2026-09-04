"""Persistent page assignments for an already-printed commentary binder."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR
from pathlib import Path
import re
import tempfile

import yaml

from .content import PIN_ID_PATTERN
from .paths import CONTENT, MANUAL


PAGE_LABEL_PATTERN = re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?")
class ManualError(ValueError):
    """Raised when the printed-manual manifest is invalid."""


@dataclass(frozen=True)
class ManualEntry:
    game_id: str
    pages: tuple[str, str]


@dataclass(frozen=True)
class Manual:
    version: int
    games: tuple[ManualEntry, ...]

    def index(self, game_id):
        for index, entry in enumerate(self.games):
            if entry.game_id == game_id:
                return index
        raise ManualError(f"game is not in the printed manual: {game_id}")

    def entry(self, game_id):
        return self.games[self.index(game_id)]


def _page_value(label):
    if not isinstance(label, str) or PAGE_LABEL_PATTERN.fullmatch(label) is None:
        raise ManualError(
            f"invalid page label {label!r}; use a positive integer or decimal string"
        )
    try:
        value = Decimal(label)
    except InvalidOperation as error:
        raise ManualError(f"invalid page label: {label!r}") from error
    if value <= 0:
        raise ManualError(f"page labels must be positive: {label!r}")
    return value


def manual_from_data(data, content_directory=CONTENT, require_content=True):
    if not isinstance(data, dict):
        raise ManualError("manual.yaml must contain a mapping")
    expected = {"version", "games"}
    actual = set(data)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        details = []
        if missing:
            details.append("missing keys: " + ", ".join(missing))
        if extra:
            details.append("unknown keys: " + ", ".join(extra))
        raise ManualError("; ".join(details))
    if data["version"] != 1:
        raise ManualError("manual version must be 1")
    if not isinstance(data["games"], list):
        raise ManualError("games must be a list")

    entries = []
    seen_ids = set()
    previous_page = None
    for position, item in enumerate(data["games"], start=1):
        if not isinstance(item, dict) or set(item) != {"id", "pages"}:
            raise ManualError(
                f"games entry {position} must contain exactly id and pages"
            )
        game_id = item["id"]
        if not isinstance(game_id, str) or PIN_ID_PATTERN.fullmatch(game_id) is None:
            raise ManualError(f"games entry {position} has an invalid id: {game_id!r}")
        if game_id in seen_ids:
            raise ManualError(f"duplicate game id in manual: {game_id}")
        seen_ids.add(game_id)
        if require_content and not (content_directory / f"{game_id}.yaml").is_file():
            raise ManualError(f"manual game has no content file: {game_id}")

        pages = item["pages"]
        if not isinstance(pages, list) or len(pages) != 2:
            raise ManualError(f"{game_id} must have exactly two page labels")
        page_values = [_page_value(label) for label in pages]
        if page_values[0] >= page_values[1]:
            raise ManualError(f"page labels for {game_id} must be increasing")
        if previous_page is not None and page_values[0] <= previous_page:
            raise ManualError(
                f"page labels are not increasing before {game_id}: {pages[0]}"
            )
        previous_page = page_values[1]
        entries.append(ManualEntry(game_id, (pages[0], pages[1])))

    return Manual(1, tuple(entries))


def load_manual(path=MANUAL, content_directory=CONTENT, require_content=True):
    try:
        with path.open("r", encoding="utf-8") as stream:
            data = yaml.safe_load(stream)
    except OSError as error:
        raise ManualError(f"could not read printed-manual manifest {path}: {error}") from error
    except yaml.YAMLError as error:
        raise ManualError(f"invalid YAML in {path}: {error}") from error
    return manual_from_data(data, content_directory, require_content)


def manual_data(manual):
    return {
        "version": manual.version,
        "games": [
            {"id": entry.game_id, "pages": list(entry.pages)}
            for entry in manual.games
        ],
    }


def write_manual(manual, path=MANUAL):
    """Validate and replace the manifest without leaving a partial file."""
    data = manual_data(manual)
    manual_from_data(data, require_content=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix=f".{path.name}-",
        suffix=".tmp",
        dir=path.parent,
        delete=False,
    ) as temporary:
        yaml.safe_dump(data, temporary, sort_keys=False, allow_unicode=True)
        temporary_path = Path(temporary.name)
    temporary_path.replace(path)


def _format_tick(tick, decimal_places):
    if decimal_places == 0:
        return str(tick)
    digits = str(tick).zfill(decimal_places + 1)
    return f"{digits[:-decimal_places]}.{digits[-decimal_places:]}"


def allocate_page_labels(left_label, right_label=None):
    """Return two stable decimal labels strictly between neighboring leaves."""
    left = _page_value(left_label)
    right = _page_value(right_label) if right_label is not None else None
    if right is None:
        right = left.to_integral_value(rounding=ROUND_CEILING)
        if right <= left:
            right += 1
    if left >= right:
        raise ManualError(f"cannot allocate pages between {left_label} and {right_label}")

    for decimal_places in range(1, 13):
        scale = Decimal(10) ** decimal_places
        first_tick = int((left * scale).to_integral_value(rounding=ROUND_FLOOR)) + 1
        last_tick = int((right * scale).to_integral_value(rounding=ROUND_CEILING)) - 1
        if last_tick - first_tick + 1 >= 2:
            return (
                _format_tick(first_tick, decimal_places),
                _format_tick(first_tick + 1, decimal_places),
            )
    raise ManualError("page labels are too densely allocated; manual intervention is required")


def insert_game(manual, game_id, index):
    if any(entry.game_id == game_id for entry in manual.games):
        raise ManualError(f"game is already in the printed manual: {game_id}")
    if index < 0 or index > len(manual.games):
        raise ManualError(f"invalid insertion position: {index}")
    left_label = manual.games[index - 1].pages[1] if index else "1"
    right_label = manual.games[index].pages[0] if index < len(manual.games) else None
    pages = allocate_page_labels(left_label, right_label)
    entries = list(manual.games)
    entries.insert(index, ManualEntry(game_id, pages))
    return Manual(manual.version, tuple(entries))


def content_paths_for_manual(path=MANUAL, content_directory=CONTENT):
    manual = load_manual(path, content_directory)
    return [content_directory / f"{entry.game_id}.yaml" for entry in manual.games]


def suggested_insertion_index(manual, game_id):
    for index, entry in enumerate(manual.games):
        if game_id < entry.game_id:
            return index
    return len(manual.games)


def neighboring_entries(manual, game_id):
    index = manual.index(game_id)
    previous = manual.games[index - 1] if index else None
    following = manual.games[index + 1] if index + 1 < len(manual.games) else None
    return previous, following
