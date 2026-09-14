"""Discovery and lookup for the location-neutral game catalog."""

from dataclasses import dataclass
import difflib
from pathlib import Path
import re

import yaml

from .content import load_yaml, normalized_game_id
from .paths import CONTENT


class CatalogError(ValueError):
    """Raised when catalog content cannot be discovered or resolved."""


@dataclass(frozen=True)
class CatalogGame:
    game_id: str
    name: str
    manufacturer: str
    year: int | None
    path: Path


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
    }
    return aliases.get(value, value)


def _edition_identity(name, manufacturer):
    """Return a title key and canonical equivalent-trim group."""
    title = normalized_game_id(name)
    manufacturer = _manufacturer_key(manufacturer)
    if manufacturer == "stern":
        match = re.fullmatch(r"(?P<title>.+?)-(?:prem-le|premium|prem|le)", title)
        if match:
            return match.group("title"), "prem-le"
    if manufacturer == "jersey-jack":
        match = re.fullmatch(r"(?P<title>.+?)-(?:le-ce|le|ce)", title)
        if match:
            return match.group("title"), "le-ce"
    return title, None


def canonical_game_key(name, manufacturer, year):
    title, trim = _edition_identity(name, manufacturer)
    manufacturer = _manufacturer_key(manufacturer)
    if (
        manufacturer == "stern"
        and title == "batman-66-catwoman-signature-edition"
        and year == 2019
    ):
        title, trim, year = "batman-66", "prem-le", 2016
    return title, trim, manufacturer, year


def match_imported_game(imported, catalog):
    """Return one conservative match, including equivalent modern trim groups."""
    imported_key = canonical_game_key(
        imported.name,
        imported.manufacturer,
        imported.year,
    )
    candidates = [
        game
        for game in catalog.values()
        if canonical_game_key(game.name, game.manufacturer, game.year) == imported_key
    ]
    return candidates[0] if len(candidates) == 1 else None


def similar_catalog_games(
    query,
    catalog=None,
    *,
    manufacturer=None,
    year=None,
    limit=8,
    threshold=0.48,
):
    """Return likely related games for a human identity check before adding."""
    catalog = catalog_by_id() if catalog is None else catalog
    query_title, query_trim = _edition_identity(query, manufacturer or "")
    query_tokens = set(query_title.split("-"))
    candidates = []
    for game in catalog.values():
        game_title, game_trim = _edition_identity(game.name, game.manufacturer)
        sequence = difflib.SequenceMatcher(None, query_title, game_title).ratio()
        game_tokens = set(game_title.split("-"))
        union = query_tokens | game_tokens
        overlap = len(query_tokens & game_tokens) / len(union) if union else 0
        score = max(sequence, overlap)
        if manufacturer and _manufacturer_key(manufacturer) == _manufacturer_key(game.manufacturer):
            score += 0.12
        if year is not None and year == game.year:
            score += 0.10
        if query_trim is not None and query_trim == game_trim:
            score += 0.10
        if score >= threshold:
            candidates.append((score, game.name.casefold(), game))
    candidates.sort(key=lambda item: (-item[0], item[1], item[2].game_id))
    return [item[2] for item in candidates[:limit]]


def content_paths(content_directory=CONTENT):
    """Return catalog content sorted by display name, then ID."""
    games = load_catalog(content_directory)
    return [game.path for game in games]


def load_catalog(content_directory=CONTENT):
    games = []
    for path in content_directory.glob("*.yaml"):
        try:
            data = load_yaml(path)
        except (OSError, yaml.YAMLError) as error:
            raise CatalogError(f"could not read catalog game {path}: {error}") from error
        if not isinstance(data, dict):
            raise CatalogError(f"catalog game must be a mapping: {path}")
        metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
        games.append(
            CatalogGame(
                game_id=data.get("id", path.stem),
                name=data.get("name", path.stem),
                manufacturer=str(metadata.get("manufacturer", "")),
                year=metadata.get("year") if isinstance(metadata.get("year"), int) else None,
                path=path,
            )
        )
    identities = {}
    for game in games:
        key = canonical_game_key(game.name, game.manufacturer, game.year)
        if key in identities:
            raise CatalogError(
                "equivalent catalog games must be deduplicated: "
                f"{identities[key]} and {game.game_id}"
            )
        identities[key] = game.game_id
    return sorted(games, key=lambda game: (game.name.casefold(), game.game_id))


def catalog_by_id(content_directory=CONTENT):
    return {game.game_id: game for game in load_catalog(content_directory)}


def resolve_game(query, content_directory=CONTENT):
    """Resolve one exact ID or unambiguous name fragment."""
    query = query.strip()
    if not query:
        return None
    games = load_catalog(content_directory)
    exact = [game for game in games if game.game_id == query]
    if exact:
        return exact[0]
    normalized = normalized_game_id(query)
    normalized_exact = [
        game
        for game in games
        if normalized_game_id(game.name) == normalized
        or normalized_game_id(game.game_id) == normalized
    ]
    if len(normalized_exact) == 1:
        return normalized_exact[0]
    matches = [
        game
        for game in games
        if query.casefold() in game.name.casefold() or query in game.game_id
    ]
    return matches[0] if len(matches) == 1 else None
