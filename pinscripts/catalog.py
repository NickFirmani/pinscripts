"""Discovery and lookup for the location-neutral game catalog."""

from dataclasses import dataclass
from pathlib import Path

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
