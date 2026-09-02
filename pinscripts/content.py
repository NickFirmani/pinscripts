"""Content loading, identifiers, registry selection, and schema validation."""

import difflib
import json
import re
import unicodedata
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from .paths import CONTENT, MANIFEST, RESEARCH, SCHEMA


PIN_ID_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


class PinRegistryError(ValueError):
    pass


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_pin_registry():
    try:
        registry = load_yaml(MANIFEST)
    except yaml.YAMLError as error:
        raise PinRegistryError(f"invalid YAML: {error}") from error

    if not isinstance(registry, dict):
        raise PinRegistryError("the document must be a mapping")

    expected_keys = {"enabled", "disabled"}
    actual_keys = set(registry)
    if actual_keys != expected_keys:
        missing = sorted(expected_keys - actual_keys)
        extra = sorted(actual_keys - expected_keys)
        details = []
        if missing:
            details.append(f"missing keys: {', '.join(missing)}")
        if extra:
            details.append(f"unknown keys: {', '.join(extra)}")
        raise PinRegistryError("; ".join(details))

    for list_name in ("enabled", "disabled"):
        pin_ids = registry[list_name]
        if not isinstance(pin_ids, list):
            raise PinRegistryError(f"{list_name} must be a list")

        invalid_ids = [
            pin_id
            for pin_id in pin_ids
            if not isinstance(pin_id, str)
            or PIN_ID_PATTERN.fullmatch(pin_id) is None
        ]
        if invalid_ids:
            raise PinRegistryError(
                f"{list_name} contains invalid pin IDs: "
                + ", ".join(repr(pin_id) for pin_id in invalid_ids)
            )

        duplicates = sorted({
            pin_id
            for pin_id in pin_ids
            if pin_ids.count(pin_id) > 1
        })
        if duplicates:
            raise PinRegistryError(
                f"{list_name} contains duplicate pin IDs: "
                + ", ".join(duplicates)
            )

    overlap = sorted(set(registry["enabled"]) & set(registry["disabled"]))
    if overlap:
        raise PinRegistryError(
            "pin IDs cannot be both enabled and disabled: "
            + ", ".join(overlap)
        )

    return registry


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
    return [f"{error_path(error)}: {error.message}" for error in errors]


def validate_content(path: Path, validator):
    try:
        data = load_yaml(path)
    except yaml.YAMLError as error:
        return [f"invalid YAML: {error}"]
    return validation_errors(data, validator)


def content_for_selected_pins():
    registry = load_pin_registry()
    enabled = registry["enabled"]
    disabled = set(registry["disabled"])

    if enabled:
        missing = [
            pin_id
            for pin_id in enabled
            if not (CONTENT / f"{pin_id}.yaml").is_file()
        ]
        if missing:
            raise PinRegistryError(
                "enabled pin IDs have no content file: " + ", ".join(missing)
            )
        selected = enabled
    else:
        selected = sorted(
            path.stem
            for path in CONTENT.glob("*.yaml")
            if path.stem not in disabled
        )

    return [CONTENT / f"{pin_id}.yaml" for pin_id in selected]
