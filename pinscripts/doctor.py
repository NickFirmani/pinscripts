"""Project health checks and guided repairs."""

from dataclasses import dataclass
from pathlib import Path
import shutil

from PIL import Image, UnidentifiedImageError
import yaml

from .binder import BinderError, load_binder
from .catalog import CatalogError, load_catalog
from .content import load_yaml, schema_validator, validate_content
from .game_workflows import interactive_add_game
from .images import (
    MIN_IMAGE_LONG_EDGE,
    interactive_black_and_white_images,
    interactive_game_image,
    interactive_low_resolution_image_repair,
)
from .locks import claim_lock
from .paths import BINDERS, CONTENT, IMAGES, ROOT, SHOT_LABELS
from .shot_labels import interactive_shot_labels, shot_label_issue


CATEGORY_ORDER = (
    "Environment",
    "Catalog",
    "Images",
    "Shot labels",
    "Binders",
    "Hygiene",
)


class DoctorInputError(ValueError):
    """Raised when a requested doctor scope does not exist."""


@dataclass(frozen=True)
class DoctorIssue:
    category: str
    code: str
    subject: str
    message: str
    command: str | None = None
    actionable: bool = True


@dataclass(frozen=True)
class DoctorReport:
    games: tuple
    binders: tuple
    issues: tuple[DoctorIssue, ...]

    @property
    def actionable_issues(self):
        return tuple(issue for issue in self.issues if issue.actionable)


def _image_details(path):
    with Image.open(path) as image:
        details = image.size, image.format
        image.verify()
        return details


def _catalog_issues(games, validator):
    issues = []
    for game in games:
        errors = validate_content(game.path, validator)
        try:
            data = load_yaml(game.path)
        except (OSError, yaml.YAMLError):
            data = None
        if isinstance(data, dict) and data.get("id") != game.path.stem:
            errors.append(
                f"$.id: expected {game.path.stem!r} to match the filename, "
                f"got {data.get('id')!r}"
            )
        for error in errors:
            issues.append(
                DoctorIssue("Catalog", "invalid-content", game.game_id, error)
            )
    return issues


def _asset_issues(games, root, images_directory, labels_directory):
    issues = []
    for game in games:
        color = images_directory / f"{game.game_id}.webp"
        color_details = None
        if not color.is_file():
            issues.append(
                DoctorIssue(
                    "Images",
                    "missing-color",
                    game.game_id,
                    f"missing {color.relative_to(root)}",
                    f"make game-image GAME={game.game_id}",
                )
            )
        else:
            try:
                color_details = _image_details(color)
            except (OSError, UnidentifiedImageError) as error:
                issues.append(
                    DoctorIssue(
                        "Images",
                        "invalid-color",
                        game.game_id,
                        f"cannot read {color.relative_to(root)}: {error}",
                        f"make game-image GAME={game.game_id}",
                    )
                )
            else:
                (width, height), image_format = color_details
                if image_format != "WEBP":
                    issues.append(
                        DoctorIssue(
                            "Images",
                            "invalid-color",
                            game.game_id,
                            f"{color.relative_to(root)} contains {image_format or 'unknown'} data, not WebP",
                            f"make game-image GAME={game.game_id}",
                        )
                    )
                if max(width, height) < MIN_IMAGE_LONG_EDGE:
                    issues.append(
                        DoctorIssue(
                            "Images",
                            "low-resolution-color",
                            game.game_id,
                            f"color image is {width}x{height}; long edge should be at least {MIN_IMAGE_LONG_EDGE}px",
                            f"make game-image GAME={game.game_id} ACTION=upgrade",
                        )
                    )
        black_and_white = images_directory / f"{game.game_id}-bw.webp"
        if color_details is not None:
            if not black_and_white.is_file():
                issues.append(
                    DoctorIssue(
                        "Images",
                        "missing-bw",
                        game.game_id,
                        f"missing {black_and_white.relative_to(root)}",
                        f"make game-image GAME={game.game_id} ACTION=bw",
                    )
                )
            else:
                try:
                    bw_details = _image_details(black_and_white)
                except (OSError, UnidentifiedImageError) as error:
                    issues.append(
                        DoctorIssue(
                            "Images",
                            "invalid-bw",
                            game.game_id,
                            f"cannot read {black_and_white.relative_to(root)}: {error}",
                            f"make game-image GAME={game.game_id} ACTION=bw",
                        )
                    )
                else:
                    _bw_size, image_format = bw_details
                    if image_format != "WEBP":
                        issues.append(
                            DoctorIssue(
                                "Images",
                                "invalid-bw",
                                game.game_id,
                                f"{black_and_white.relative_to(root)} contains {image_format or 'unknown'} data, not WebP",
                                f"make game-image GAME={game.game_id} ACTION=bw",
                            )
                        )

        try:
            data = load_yaml(game.path)
            label_problem = shot_label_issue(
                data,
                root=root,
                labels_directory=labels_directory,
            )
        except (KeyError, OSError, yaml.YAMLError) as error:
            label_problem = str(error)
        if label_problem:
            issues.append(
                DoctorIssue(
                    "Shot labels",
                    "shot-labels",
                    game.game_id,
                    label_problem,
                    f"make game-labels GAME={game.game_id}",
                )
            )
    return issues


def _load_binders(binder_id, binders_directory, content_directory):
    if binder_id:
        try:
            return (
                load_binder(
                    binder_id,
                    binders_directory=binders_directory,
                    content_directory=content_directory,
                ),
            ), ()
        except BinderError as error:
            path = binders_directory / f"{binder_id}.yaml"
            if not path.exists():
                raise DoctorInputError(f"no binder manifest: {path}") from error
            return (), (
                DoctorIssue("Binders", "invalid-binder", binder_id, str(error)),
            )

    binders = []
    issues = []
    for path in sorted(binders_directory.glob("*.yaml")):
        try:
            binders.append(
                load_binder(
                    path,
                    binders_directory=binders_directory,
                    content_directory=content_directory,
                )
            )
        except BinderError as error:
            issues.append(
                DoctorIssue("Binders", "invalid-binder", path.stem, str(error))
            )
    return tuple(binders), tuple(issues)


def _binder_issues(binders):
    issues = []
    for binder in binders:
        if binder.pending_games:
            issues.append(
                DoctorIssue(
                    "Binders",
                    "pending-games",
                    binder.binder_id,
                    f"{len(binder.pending_games)} unresolved imported game(s)",
                    f"make binder-populate BINDER={binder.binder_id}",
                )
            )
    return issues


def _hygiene_issues(game_ids, images_directory, labels_directory):
    issues = []
    for path in sorted(images_directory.glob("*.webp")):
        image_id = path.stem.removesuffix("-bw")
        if image_id not in game_ids:
            issues.append(
                DoctorIssue(
                    "Hygiene",
                    "orphan-image",
                    path.name,
                    "image has no catalog game",
                    actionable=False,
                )
            )
    for path in sorted(labels_directory.glob("*.yaml")):
        if path.stem not in game_ids:
            issues.append(
                DoctorIssue(
                    "Hygiene",
                    "orphan-labels",
                    path.name,
                    "shot-label file has no catalog game",
                    actionable=False,
                )
            )
    return issues


def scan_project(
    game_id=None,
    binder_id=None,
    *,
    root=ROOT,
    content_directory=CONTENT,
    images_directory=IMAGES,
    labels_directory=SHOT_LABELS,
    binders_directory=BINDERS,
):
    if game_id and binder_id:
        raise DoctorInputError("use either GAME or BINDER, not both")

    issues = []
    try:
        all_games = tuple(load_catalog(content_directory))
    except CatalogError as error:
        return DoctorReport(
            (),
            (),
            (DoctorIssue("Catalog", "invalid-catalog", "catalog", str(error)),),
        )

    games_by_id = {game.game_id: game for game in all_games}
    if game_id:
        binders, binder_load_issues = (), ()
    else:
        binders, binder_load_issues = _load_binders(
            binder_id,
            binders_directory,
            content_directory,
        )
    issues.extend(binder_load_issues)

    if game_id:
        if game_id not in games_by_id:
            raise DoctorInputError(f"no catalog game: {game_id}")
        games = (games_by_id[game_id],)
    elif binder_id and binders:
        games = tuple(
            games_by_id[entry.game_id]
            for entry in binders[0].active_games
            if entry.game_id in games_by_id
        )
    elif binder_id:
        games = ()
    else:
        games = all_games

    issues.extend(_catalog_issues(games, schema_validator()))
    issues.extend(_asset_issues(games, root, images_directory, labels_directory))
    issues.extend(_binder_issues(binders))

    if not game_id and not binder_id:
        issues.extend(
            _hygiene_issues(set(games_by_id), images_directory, labels_directory)
        )
        if shutil.which("magick") is None and shutil.which("convert") is None:
            issues.append(
                DoctorIssue(
                    "Environment",
                    "missing-imagemagick",
                    "ImageMagick",
                    "not found; image creation and repair will be unavailable",
                    actionable=False,
                )
            )

    return DoctorReport(tuple(games), tuple(binders), tuple(issues))


def print_report(report):
    scope = f"{len(report.games)} game(s), {len(report.binders)} binder(s)"
    print(f"PinScripts doctor — {scope}")
    if not report.issues:
        print("\n✓ No problems found.")
        return
    for category in CATEGORY_ORDER:
        category_issues = [
            issue for issue in report.issues if issue.category == category
        ]
        if not category_issues:
            continue
        print(f"\n{category}")
        for issue in category_issues:
            marker = "✗" if issue.actionable else "⚠"
            print(f"  {marker} {issue.subject}: {issue.message}")
            if issue.command:
                print(f"    Fix: {issue.command}")
    actionable = len(report.actionable_issues)
    warnings = len(report.issues) - actionable
    print(f"\n{actionable} actionable issue(s), {warnings} warning(s).")


def _ask(question):
    try:
        answer = input(f"{question} [y/N] ")
    except EOFError:
        answer = ""
    return answer.strip().casefold() in {"y", "yes"}


def _subjects(report, codes):
    return tuple(
        dict.fromkeys(
            issue.subject for issue in report.issues if issue.code in codes
        )
    )


def _repair_games(game_ids, repair):
    for game_id in game_ids:
        with claim_lock(f"add-{game_id}", blocking=False) as claimed:
            if not claimed:
                print(f"Skipping {game_id}; another terminal is working on it.")
                continue
            repair(game_id)


def _repair_interactively(report, game_id=None, binder_id=None):
    attempted = False
    current = report

    def rescan():
        return scan_project(game_id, binder_id)

    color = _subjects(current, {"missing-color", "invalid-color"})
    if color and _ask(f"Repair {len(color)} missing or invalid color image(s) now?"):
        attempted = True
        _repair_games(
            color,
            lambda game_id: interactive_game_image(game_id, continue_batch=False),
        )
        current = rescan()

    upgrades = _subjects(
        current,
        {"low-resolution-color"},
    )
    if upgrades and _ask(f"Upgrade {len(upgrades)} low-quality color image(s) now?"):
        attempted = True
        _repair_games(upgrades, interactive_low_resolution_image_repair)
        current = rescan()

    black_and_white = _subjects(
        current,
        {"missing-bw", "invalid-bw"},
    )
    if black_and_white and _ask(
        f"Repair {len(black_and_white)} missing or invalid B&W image(s) now?"
    ):
        attempted = True
        _repair_games(black_and_white, interactive_black_and_white_images)
        current = rescan()

    labels = _subjects(current, {"shot-labels"})
    if labels and _ask(f"Repair shot labels for {len(labels)} game(s) now?"):
        attempted = True
        _repair_games(
            labels,
            lambda game_id: interactive_shot_labels(game_id, continue_batch=False),
        )
        current = rescan()

    binders = _subjects(current, {"pending-games"})
    if binders and _ask(f"Populate {len(binders)} binder(s) with pending games now?"):
        attempted = True
        for pending_binder_id in binders:
            interactive_add_game(binder_id=pending_binder_id)
        current = rescan()
    return attempted, current


def run_doctor(game_id=None, binder_id=None, *, check=False):
    report = scan_project(game_id, binder_id)
    print_report(report)
    if check or not report.actionable_issues:
        return 1 if report.actionable_issues else 0
    attempted, final_report = _repair_interactively(report, game_id, binder_id)
    if not attempted:
        return 1

    print("\nRescanning after repairs...\n")
    print_report(final_report)
    return 1 if final_report.actionable_issues else 0
