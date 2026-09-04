"""Content loading, identifiers, and schema validation."""

import difflib
import json
import re
import unicodedata
from datetime import date
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from .paths import RESEARCH, SCHEMA


PIN_ID_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_schema():
    with SCHEMA.open("r", encoding="utf-8") as file:
        return json.load(file)


def schema_validator():
    schema = load_schema()
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def suggested_research_id(game):
    return re.sub(r"[^a-z0-9]+", "-", game.lower()).strip("-")


def normalized_game_id(game):
    """Normalize common display-name variants for research ID matching."""
    normalized = unicodedata.normalize("NFKD", game)
    normalized = normalized.encode("ascii", "ignore").decode("ascii").lower()
    normalized = normalized.replace("&", " and ")
    normalized = re.sub(r"['\u2019]", "", normalized)
    normalized = re.sub(r"\blimited edition\b", "le", normalized)
    normalized = re.sub(r"\bspecial edition\b", "se", normalized)
    normalized = re.sub(r"\bgold edition\b", "gold", normalized)
    normalized = re.sub(r"\bthe\b", " ", normalized)
    return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")


def matching_research_id(game, research_directory=None):
    research_directory = research_directory or RESEARCH
    research_ids = sorted(path.stem for path in research_directory.glob("*.md"))
    derived_id = suggested_research_id(game)
    if derived_id in research_ids:
        return derived_id

    normalized_id = normalized_game_id(game)
    if normalized_id in research_ids:
        return normalized_id

    game_tokens = set(normalized_id.split("-"))
    game_years = {token for token in game_tokens if re.fullmatch(r"\d{4}", token)}
    candidates = []
    for research_id in research_ids:
        comparable_id = normalized_game_id(research_id)
        research_tokens = set(comparable_id.split("-"))
        research_years = {
            token for token in research_tokens if re.fullmatch(r"\d{4}", token)
        }
        if game_years and research_years and game_years != research_years:
            continue

        overlap = len(game_tokens & research_tokens)
        if not overlap:
            continue
        precision = overlap / len(research_tokens)
        coverage = overlap / len(game_tokens)
        sequence = difflib.SequenceMatcher(
            None, normalized_id, comparable_id
        ).ratio()
        score = 0.65 * precision + 0.20 * sequence + 0.15 * coverage
        if precision >= 0.75 and score >= 0.72:
            candidates.append((score, research_id))

    candidates.sort(reverse=True)
    if not candidates:
        return None
    if len(candidates) > 1 and candidates[0][0] - candidates[1][0] < 0.05:
        return None
    return candidates[0][1]


def error_path(error):
    path = "$"
    for part in error.absolute_path:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return path


def validation_errors(data, validator):
    errors = sorted(
        validator.iter_errors(data),
        key=lambda error: [str(part) for part in error.absolute_path],
    )
    messages = [f"{error_path(error)}: {error.message}" for error in errors]
    messages.extend(rules_basis_errors(data))
    return messages


def rules_basis_errors(data):
    """Validate relationships intentionally kept out of the strict JSON schema."""
    if not isinstance(data, dict):
        return []

    basis = data.get("rules_basis")
    if not isinstance(basis, dict):
        return []

    kind = basis.get("kind")
    version = basis.get("version")
    release_date = basis.get("release_date")
    errors = []

    if kind in {"code", "rom"} and not (
        isinstance(version, str) and version.strip()
    ):
        errors.append(
            f"$.rules_basis.version: {kind} rules require a non-empty version"
        )
    if kind == "fixed" and version is not None:
        errors.append("$.rules_basis.version: fixed rules require null")

    if kind == "code":
        if not isinstance(release_date, str):
            errors.append(
                "$.rules_basis.release_date: downloadable code requires a release date"
            )
        else:
            try:
                date.fromisoformat(release_date)
            except ValueError:
                errors.append(
                    "$.rules_basis.release_date: must be a valid YYYY-MM-DD date"
                )
    elif kind in {"rom", "fixed"} and release_date is not None:
        errors.append(f"$.rules_basis.release_date: {kind} rules require null")

    return errors


def validate_content(path: Path, validator):
    try:
        data = load_yaml(path)
    except yaml.YAMLError as error:
        return [f"invalid YAML: {error}"]
    return validation_errors(data, validator)
