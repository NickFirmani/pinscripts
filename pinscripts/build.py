"""Validation, PDF rendering, and binder assembly workflows."""

import sys

from .pdf import merge_pdfs, render_game

from .content import (
    PinRegistryError,
    content_for_selected_pins,
    load_yaml,
    schema_validator,
    validate_content,
)
from .paths import CONTENT, MANIFEST, OUTPUT
from .shot_labels import ShotLabelError, load_shot_labels


class BuildInputError(ValueError):
    pass


def validate_all(paths):
    validator = schema_validator()
    valid = True

    for path in paths:
        errors = validate_content(path, validator)
        if not errors:
            try:
                data = load_yaml(path)
                load_shot_labels(data)
            except ShotLabelError as error:
                errors.append(
                    f"shot labels: {error}; run "
                    f"make shot-labels GAME=\"{data.get('id', path.stem)}\""
                )
        if errors:
            valid = False
            print(f"ERROR: validation failed: {path}", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        else:
            print(f"Validated {path}")

    return valid


def render(paths, black_and_white=False):
    output_suffix = "-bw" if black_and_white else ""
    for path in paths:
        render_game(
            path,
            OUTPUT / f"{path.stem}{output_suffix}.pdf",
            black_and_white,
        )


def build_paths(paths, black_and_white=False, binder=False):
    if not validate_all(paths):
        return 1

    render(paths, black_and_white)
    if binder:
        output_suffix = "-bw" if black_and_white else ""
        pdfs = [OUTPUT / f"{path.stem}{output_suffix}.pdf" for path in paths]
        merge_pdfs(pdfs, OUTPUT / f"binder{output_suffix}.pdf")
    return 0


def build_game(game_id, black_and_white=False):
    path = CONTENT / f"{game_id}.yaml"
    if not path.exists():
        raise BuildInputError(f"no content file: {path}")
    return build_paths([path], black_and_white)


def build_selected(black_and_white=False, binder=False):
    try:
        paths = content_for_selected_pins()
    except PinRegistryError as error:
        print(f"ERROR: invalid {MANIFEST}: {error}", file=sys.stderr)
        return 1
    return build_paths(paths, black_and_white, binder)
