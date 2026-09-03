#!/usr/bin/env python3
"""Audit rules-basis metadata across all game content files."""

import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pinscripts.content import load_yaml, rules_basis_errors, schema_validator  # noqa: E402
from pinscripts.paths import CONTENT  # noqa: E402


def audit_file(path, validator):
    try:
        data = load_yaml(path)
    except (OSError, yaml.YAMLError) as error:
        return [f"could not load YAML: {error}"]

    if not isinstance(data, dict):
        return ["$: game content must be an object"]

    errors = []
    for error in validator.iter_errors(data):
        if "rules_basis" in error.absolute_path or (
            error.validator == "required"
            and "rules_basis" in error.message
        ):
            location = "$"
            for part in error.absolute_path:
                location += f"[{part}]" if isinstance(part, int) else f".{part}"
            errors.append(f"{location}: {error.message}")
    errors.extend(rules_basis_errors(data))
    return errors


def main():
    validator = schema_validator()
    paths = sorted(CONTENT.glob("*.yaml"))
    failures = 0
    counts = {"code": 0, "rom": 0, "fixed": 0}

    for path in paths:
        errors = audit_file(path, validator)
        if errors:
            failures += 1
            print(f"ERROR: {path}", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            continue

        kind = load_yaml(path)["rules_basis"]["kind"]
        counts[kind] += 1

    print(
        f"Audited {len(paths)} games: "
        f"{counts['code']} code, {counts['rom']} ROM, {counts['fixed']} fixed."
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
