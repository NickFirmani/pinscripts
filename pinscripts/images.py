"""Image discovery, acquisition, repair, and black-and-white workflows."""

import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlencode

from PIL import Image, UnidentifiedImageError

from scripts.process_images import VARIANTS, process_images, require_imagemagick

from .content import matching_research_id, suggested_research_id
from .interaction import confirm_overwrite
from .paths import DOWNLOADS, GAME_LIST, IMAGES, RESEARCH, ROOT


DOWNLOAD_IMAGE_SUFFIXES = {
    ".avif", ".bmp", ".gif", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp",
}
CANONICAL_IMAGE_SUFFIX = ".webp"
MIN_IMAGE_LONG_EDGE = 1000
BLACK_AND_WHITE_PREFETCH = 2
PLAYFIELD_ASPECT_WIDTH = 408
PLAYFIELD_ASPECT_HEIGHT = 750
PLAYFIELD_ASPECT_TOLERANCE = 0.01
SIMPLIFIED_ASPECT_WIDTH = 68
SIMPLIFIED_ASPECT_HEIGHT = 125
XNVIEWMP_APPLICATION_NAMES = ("XnViewMP", "XnView MP")


def image_id_for_game(game, research_directory=None):
    research_directory = research_directory or RESEARCH
    return matching_research_id(game, research_directory) or suggested_research_id(game)


def first_game_without_image(
    game_list=None,
    images_directory=None,
    research_directory=None,
):
    game_list = game_list or GAME_LIST
    images_directory = images_directory or IMAGES
    games = [
        line.strip()
        for line in game_list.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for game in games:
        image_id = image_id_for_game(game, research_directory)
        has_image = (images_directory / f"{image_id}{CANONICAL_IMAGE_SUFFIX}").is_file()
        if not has_image:
            return game
    return None


def black_and_white_pair(source, images_directory=None):
    images_directory = images_directory or IMAGES
    candidate = images_directory / f"{source.stem}-bw{CANONICAL_IMAGE_SUFFIX}"
    return candidate if candidate.is_file() else None


def color_images_without_black_and_white(images_directory=None):
    images_directory = images_directory or IMAGES
    try:
        paths = images_directory.iterdir()
    except OSError:
        return []
    color_images = sorted(
        path
        for path in paths
        if path.is_file()
        and not path.name.startswith(".")
        and not path.stem.endswith("-bw")
        and path.suffix.lower() == CANONICAL_IMAGE_SUFFIX
    )
    return [
        source
        for source in color_images
        if black_and_white_pair(source, images_directory) is None
    ]


def find_color_image(game, images_directory=None, research_directory=None):
    images_directory = images_directory or IMAGES
    supplied_path = Path(game).expanduser()
    if supplied_path.is_file():
        return (
            supplied_path
            if supplied_path.suffix.lower() == CANONICAL_IMAGE_SUFFIX
            else None
        )
    image_id = image_id_for_game(game, research_directory)
    candidate = images_directory / f"{image_id}{CANONICAL_IMAGE_SUFFIX}"
    return candidate if candidate.is_file() else None


def open_images_in_preview(paths):
    subprocess.run(
        ["open", "-a", "Preview", *(str(path) for path in paths)],
        check=True,
    )


def find_xnviewmp_application():
    """Return the macOS application name when XnView MP is installed."""
    for application in XNVIEWMP_APPLICATION_NAMES:
        try:
            result = subprocess.run(
                ["open", "-Ra", application],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except OSError:
            return None
        if result.returncode == 0:
            return application
    return None


def suggested_crop_size(width, height):
    """Return the largest exact 408:750 crop that fits the image."""
    scale = min(
        width // SIMPLIFIED_ASPECT_WIDTH,
        height // SIMPLIFIED_ASPECT_HEIGHT,
    )
    if scale < 1:
        raise ValueError(
            "image is too small for an exact 408:750 integer-pixel crop"
        )
    return SIMPLIFIED_ASPECT_WIDTH * scale, SIMPLIFIED_ASPECT_HEIGHT * scale


def has_playfield_aspect_ratio(width, height):
    if width <= 0 or height <= 0:
        return False
    target_ratio = PLAYFIELD_ASPECT_WIDTH / PLAYFIELD_ASPECT_HEIGHT
    actual_ratio = width / height
    relative_error = abs(actual_ratio - target_ratio) / target_ratio
    return relative_error <= PLAYFIELD_ASPECT_TOLERANCE


def prepare_downloaded_image_for_crop(path):
    """Open a crop editor and verify that the saved image is exactly 408:750."""
    try:
        width, height = image_dimensions(path)
        crop_width, crop_height = suggested_crop_size(width, height)
    except (OSError, UnidentifiedImageError, ValueError) as error:
        print(f"ERROR: could not prepare {path.name} for cropping: {error}", file=sys.stderr)
        return False

    if has_playfield_aspect_ratio(width, height):
        print(f"Image already has the required 408:750 aspect ratio ({width}x{height}).")
        return True

    application = find_xnviewmp_application()
    try:
        if application:
            subprocess.run(["open", "-a", application, str(path)], check=True)
            print(
                f"Opened {path.name} in {application}. Crop it to a fixed "
                "408:750 aspect ratio and save the file in place."
            )
        else:
            open_images_in_preview([path])
            print(
                f"XnView MP was not found, so {path.name} was opened in Preview."
            )
            print(
                f"For this {width}x{height} image, use a centered "
                f"{crop_width}x{crop_height} pixel selection, then crop and save."
            )
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"ERROR: could not open an image crop editor: {error}", file=sys.stderr)
        return False

    while True:
        try:
            answer = input(
                "After cropping and saving the downloaded image, press Enter "
                "to verify it (or enter q to cancel): "
            )
        except EOFError:
            answer = "q"
        if answer.strip().lower() in {"q", "quit"}:
            print("Image crop cancelled.", file=sys.stderr)
            return False
        try:
            cropped_width, cropped_height = image_dimensions(path)
        except (OSError, UnidentifiedImageError) as error:
            print(f"ERROR: could not inspect the cropped image: {error}", file=sys.stderr)
            return False
        if has_playfield_aspect_ratio(cropped_width, cropped_height):
            print(
                "Confirmed 408:750 crop: "
                f"{cropped_width}x{cropped_height}."
            )
            return True
        try:
            next_width, next_height = suggested_crop_size(
                cropped_width,
                cropped_height,
            )
        except ValueError as error:
            print(f"ERROR: {error}", file=sys.stderr)
            return False
        print(
            f"The saved image is {cropped_width}x{cropped_height}, which is not "
            "408:750. Crop again using a centered "
            f"{next_width}x{next_height} pixel selection.",
            file=sys.stderr,
        )


def request_black_and_white_variant(variant_paths):
    print("\nBlack-and-white candidates:")
    names = list(VARIANTS)
    for index, name in enumerate(names, start=1):
        print(f"  {index}. {name}: {variant_paths[index - 1].name}")
    while True:
        try:
            answer = input(
                f"Choose the best variant [1-{len(names)}], "
                "enter its name, s to skip, or q to quit: "
            ).strip().lower()
        except EOFError:
            return "quit", None
        if answer in {"q", "quit"}:
            return "quit", None
        if answer in {"s", "skip"}:
            return "skip", None
        if answer in names:
            return "selected", variant_paths[names.index(answer)]
        if answer.isdigit() and 1 <= int(answer) <= len(names):
            return "selected", variant_paths[int(answer) - 1]
        print("Enter a listed number or name, s, or q.", file=sys.stderr)


class MissingImageVariantsError(RuntimeError):
    pass


def generate_black_and_white_variants(source, output_directory, show_progress=True):
    output_dir = process_images(source, output_directory, show_progress=show_progress)
    variant_paths = [output_dir / f"{source.stem}-{name}.webp" for name in VARIANTS]
    missing = [path for path in variant_paths if not path.is_file()]
    if missing:
        raise MissingImageVariantsError(
            "image processing did not create: "
            + ", ".join(path.name for path in missing)
        )
    return variant_paths


def report_black_and_white_generation_error(error):
    if isinstance(error, (SystemExit, MissingImageVariantsError)):
        print(f"ERROR: {error}", file=sys.stderr)
    else:
        print(f"ERROR: could not generate image variants: {error}", file=sys.stderr)


def review_black_and_white_variants(source, variant_paths):
    try:
        open_images_in_preview(variant_paths)
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"ERROR: could not open Preview: {error}", file=sys.stderr)
        return "error"
    action, selected = request_black_and_white_variant(variant_paths)
    if action != "selected":
        return action
    destination = black_and_white_pair(source) or (
        IMAGES / f"{source.stem}-bw{CANONICAL_IMAGE_SUFFIX}"
    )
    if not confirm_overwrite(destination):
        print("Black-and-white image not saved.", file=sys.stderr)
        return "skip"
    try:
        IMAGES.mkdir(parents=True, exist_ok=True)
        shutil.copy2(selected, destination)
    except OSError as error:
        print(
            f"ERROR: could not copy {selected} to {destination}: {error}",
            file=sys.stderr,
        )
        return "error"
    try:
        display_path = destination.relative_to(ROOT)
    except ValueError:
        display_path = destination
    variant_name = selected.stem[len(source.stem) + 1:]
    print(f"Saved {display_path} from the {variant_name} variant.")
    return "selected"


def process_black_and_white_image(source):
    print(f"\nGenerating candidates for {source.name}...")
    with tempfile.TemporaryDirectory(prefix=f"{source.stem}-variants-") as directory:
        try:
            variant_paths = generate_black_and_white_variants(source, Path(directory))
        except (
            SystemExit,
            MissingImageVariantsError,
            OSError,
            subprocess.CalledProcessError,
        ) as error:
            report_black_and_white_generation_error(error)
            return "error"
        return review_black_and_white_variants(source, variant_paths)


def process_black_and_white_batch(sources):
    had_error = False
    with (
        tempfile.TemporaryDirectory(prefix="bw-variants-") as directory,
        ThreadPoolExecutor(max_workers=BLACK_AND_WHITE_PREFETCH) as executor,
    ):
        batch_directory = Path(directory)
        pending = {}
        next_source = 0

        def fill_prefetch_window(current_index):
            nonlocal next_source
            stop = min(len(sources), current_index + BLACK_AND_WHITE_PREFETCH + 1)
            while next_source < stop:
                source = sources[next_source]
                print(f"\nGenerating candidates for {source.name}...")
                output_dir = batch_directory / f"{next_source}-{source.stem}"
                pending[next_source] = executor.submit(
                    generate_black_and_white_variants, source, output_dir, False
                )
                next_source += 1

        fill_prefetch_window(0)
        for index, source in enumerate(sources):
            try:
                variant_paths = pending.pop(index).result()
            except (
                SystemExit,
                MissingImageVariantsError,
                OSError,
                subprocess.CalledProcessError,
            ) as error:
                report_black_and_white_generation_error(error)
                result = "error"
            else:
                result = review_black_and_white_variants(source, variant_paths)
            if result == "quit":
                break
            if result == "error":
                had_error = True
            fill_prefetch_window(index + 1)
    return 1 if had_error else 0


def interactive_black_and_white_images(game):
    game = game.strip()
    if game:
        source = find_color_image(game)
        if source is None:
            print(f"ERROR: no color image found for {game!r}.", file=sys.stderr)
            return 1
        sources = [source]
    else:
        sources = color_images_without_black_and_white()
        if not sources:
            print("Every color image already has a black-and-white pair.")
            return 0
        print(f"Found {len(sources)} color image(s) without black-and-white pairs.")
    if not game:
        return process_black_and_white_batch(sources)
    had_error = False
    for source in sources:
        result = process_black_and_white_image(source)
        if result == "quit":
            break
        if result == "error":
            had_error = True
    return 1 if had_error else 0


def download_snapshot(downloads_directory=None):
    downloads_directory = downloads_directory or DOWNLOADS
    snapshot = {}
    try:
        paths = downloads_directory.iterdir()
    except OSError:
        return snapshot
    for path in paths:
        if path.name.startswith(".") or path.suffix.lower() == ".crdownload":
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        if path.is_file():
            snapshot[path] = (stat.st_size, stat.st_mtime_ns)
    return snapshot


def newest_download_since(snapshot, downloads_directory=None):
    downloads_directory = downloads_directory or DOWNLOADS
    candidates = []
    for path, signature in download_snapshot(downloads_directory).items():
        if snapshot.get(path) == signature:
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        birth_time = getattr(
            stat,
            "st_birthtime_ns",
            int(getattr(stat, "st_birthtime", 0) * 1_000_000_000),
        )
        candidates.append((max(stat.st_mtime_ns, birth_time), path))
    return max(candidates, default=(None, None))[1]


def image_dimensions(path):
    with Image.open(path) as image:
        return image.size


def confirm_image_resolution(path):
    try:
        width, height = image_dimensions(path)
    except (OSError, UnidentifiedImageError) as error:
        print(
            f"ERROR: downloaded file is not a readable image: {error}",
            file=sys.stderr,
        )
        return False
    print(f"Downloaded image resolution: {width}x{height}")
    if max(width, height) >= MIN_IMAGE_LONG_EDGE:
        return True
    print(
        f"WARNING: the image's long edge is below {MIN_IMAGE_LONG_EDGE}px; "
        "it may look soft in print.",
        file=sys.stderr,
    )
    try:
        answer = input("Use this low-resolution image anyway? [y/N] ")
    except EOFError:
        answer = ""
    return answer.strip().lower() in {"y", "yes"}


def low_resolution_color_images(
    images_directory=None,
    minimum_long_edge=MIN_IMAGE_LONG_EDGE,
):
    images_directory = images_directory or IMAGES
    try:
        paths = images_directory.iterdir()
    except OSError as error:
        raise OSError(f"could not read images directory {images_directory}: {error}")
    low_resolution = []
    for path in sorted(paths):
        if (
            not path.is_file()
            or path.name.startswith(".")
            or path.stem.endswith("-bw")
            or path.suffix.lower() != CANONICAL_IMAGE_SUFFIX
        ):
            continue
        try:
            width, height = image_dimensions(path)
        except (OSError, UnidentifiedImageError) as error:
            print(f"WARNING: could not inspect {path}: {error}", file=sys.stderr)
            continue
        if max(width, height) < minimum_long_edge:
            low_resolution.append((path, width, height))
    return low_resolution


def game_name_for_image(source, game_list=None, research_directory=None):
    game_list = game_list or GAME_LIST
    try:
        games = [
            line.strip()
            for line in game_list.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    except OSError:
        games = []
    for game in games:
        if image_id_for_game(game, research_directory) == source.stem:
            return game
    return source.stem.replace("-", " ")


def unused_backup_path(path, backup_directory):
    candidate = backup_directory / path.name
    index = 2
    while candidate.exists():
        candidate = backup_directory / f"{path.stem}-{index}{path.suffix}"
        index += 1
    return candidate


def write_canonical_webp(source, destination):
    """Write an arbitrary downloaded image as an atomic canonical WebP."""
    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix=f".{destination.stem}-incoming-",
        suffix=CANONICAL_IMAGE_SUFFIX,
        dir=destination.parent,
        delete=False,
    ) as temporary:
        temporary_path = Path(temporary.name)
    try:
        if source.suffix.lower() == CANONICAL_IMAGE_SUFFIX:
            shutil.copy2(source, temporary_path)
        else:
            magick = require_imagemagick()
            subprocess.run(
                [
                    magick,
                    str(source),
                    "-auto-orient",
                    "-quality",
                    "92",
                    str(temporary_path),
                ],
                check=True,
            )
        image_dimensions(temporary_path)
        temporary_path.replace(destination)
    finally:
        temporary_path.unlink(missing_ok=True)


def replace_canonical_image(download, destination):
    destination = destination.resolve()
    if destination.suffix.lower() != CANONICAL_IMAGE_SUFFIX:
        raise ValueError(f"canonical image must be WebP: {destination}")
    backup_directory = destination.parent / "low-res-backup"
    backup_directory.mkdir(parents=True, exist_ok=True)
    backup = unused_backup_path(destination, backup_directory)
    shutil.copy2(destination, backup)
    write_canonical_webp(download, destination)
    black_and_white = black_and_white_pair(destination, destination.parent)
    black_and_white_backup = None
    if black_and_white is not None:
        black_and_white_backup = unused_backup_path(
            black_and_white,
            backup_directory,
        )
        shutil.move(black_and_white, black_and_white_backup)
    return backup, black_and_white_backup


def interactive_low_resolution_image_repair(game):
    game = game.strip()
    if game:
        source = find_color_image(game)
        if source is None:
            print(f"ERROR: no color image found for {game!r}.", file=sys.stderr)
            return 1
        try:
            width, height = image_dimensions(source)
        except (OSError, UnidentifiedImageError) as error:
            print(f"ERROR: could not inspect {source}: {error}", file=sys.stderr)
            return 1
        search_name = game_name_for_image(source) if Path(game).is_file() else game
        images = [(source, width, height, search_name)]
    else:
        try:
            images = low_resolution_color_images()
        except OSError as error:
            print(f"ERROR: {error}", file=sys.stderr)
            return 1
        if not images:
            print(
                "No color images are below the "
                f"{MIN_IMAGE_LONG_EDGE}px long-edge threshold."
            )
            return 0
        images = [
            (source, width, height, game_name_for_image(source))
            for source, width, height in images
        ]

    print(
        f"Found {len(images)} image(s). Opening a Google Image search for each "
        "game in Chrome."
    )
    for index, (source, width, height, search_name) in enumerate(images, start=1):
        print(f"\n[{index}/{len(images)}] {source.name} ({width}x{height})")
        before = download_snapshot()
        try:
            open_google_image_search(search_name)
        except (OSError, subprocess.CalledProcessError) as error:
            print(
                f"ERROR: could not open Google Image search for {source}: {error}",
                file=sys.stderr,
            )
            return 1
        while True:
            try:
                answer = input(
                    "Download a better result, then press Enter to replace this "
                    "image (s to skip, q to quit): "
                )
            except EOFError:
                answer = "q"
            if answer.strip().lower() in {"q", "quit"}:
                return 0
            if answer.strip().lower() in {"s", "skip"}:
                break
            download = newest_download_since(before)
            if download is None:
                print(
                    f"No new completed file was found in {DOWNLOADS}; "
                    "download an image or skip this one.",
                    file=sys.stderr,
                )
                continue
            if not confirm_image_resolution(download):
                print(
                    "Replacement rejected; download a better image or skip this one.",
                    file=sys.stderr,
                )
                before = download_snapshot()
                continue
            if not prepare_downloaded_image_for_crop(download):
                print(
                    "Replacement rejected because its crop was not completed.",
                    file=sys.stderr,
                )
                before = download_snapshot()
                continue
            try:
                backup, black_and_white_backup = replace_canonical_image(
                    download,
                    source,
                )
            except (OSError, subprocess.CalledProcessError, SystemExit) as error:
                print(f"ERROR: could not replace {source}: {error}", file=sys.stderr)
                return 1
            new_width, new_height = image_dimensions(source)
            print(
                f"Replaced {source.name}: {width}x{height} -> "
                f"{new_width}x{new_height}; backup: {backup}"
            )
            if black_and_white_backup is not None:
                print(
                    "Moved the stale black-and-white pair to "
                    f"{black_and_white_backup}."
                )
            break
    return 0


def google_image_search_url(game):
    return "https://www.google.com/search?" + urlencode(
        {"tbm": "isch", "q": game + " playfield"}
    )


def open_google_image_search(game):
    subprocess.run(
        ["open", "-a", "Google Chrome", google_image_search_url(game)],
        check=True,
    )


def interactive_game_image(game, continue_batch=True):
    game = game.strip()
    if not game:
        try:
            game = first_game_without_image()
        except OSError as error:
            print(
                f"ERROR: could not read game list {GAME_LIST}: {error}",
                file=sys.stderr,
            )
            return 1
        if game is None:
            print(f"Every game in {GAME_LIST} already has an image.")
            return 0
        print(f"Selected first game without an image: {game}")
    if not game:
        print("ERROR: a game name is required.", file=sys.stderr)
        return 2
    if not DOWNLOADS.is_dir():
        print(
            f"ERROR: downloads directory does not exist: {DOWNLOADS}",
            file=sys.stderr,
        )
        return 1

    before = download_snapshot()
    try:
        open_google_image_search(game)
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"ERROR: could not open Google Chrome: {error}", file=sys.stderr)
        return 1
    try:
        answer = input(
            "Download the desired image in Chrome to your Downloads folder, then press Enter to copy it "
            "(or enter q to cancel): "
        )
    except EOFError:
        answer = "q"
    if answer.strip().lower() in {"q", "quit"}:
        print("Image copy cancelled.", file=sys.stderr)
        return 0

    source = newest_download_since(before)
    if source is None:
        print(
            f"ERROR: no new completed file was found in {DOWNLOADS}.",
            file=sys.stderr,
        )
        return 1
    if not confirm_image_resolution(source):
        print("Image not copied.", file=sys.stderr)
        return 0
    research_id = matching_research_id(game, RESEARCH)
    image_id = image_id_for_game(game)
    if not image_id:
        print("ERROR: could not derive an image filename.", file=sys.stderr)
        return 1
    if source.suffix.lower() not in DOWNLOAD_IMAGE_SUFFIXES:
        print(
            f"ERROR: unsupported downloaded image format: {source.suffix}",
            file=sys.stderr,
        )
        return 1
    if not prepare_downloaded_image_for_crop(source):
        print("Image not copied.", file=sys.stderr)
        return 0
    destination = IMAGES / f"{image_id}{CANONICAL_IMAGE_SUFFIX}"
    if not confirm_overwrite(destination):
        print("Image not copied.", file=sys.stderr)
        return 0
    try:
        write_canonical_webp(source, destination)
    except (OSError, subprocess.CalledProcessError, SystemExit) as error:
        print(
            f"ERROR: could not copy {source} to {destination}: {error}",
            file=sys.stderr,
        )
        return 1
    id_source = "research" if research_id else "game name"
    print(f"Copied {source} to {destination.relative_to(ROOT)} ({id_source} ID).")
    if continue_batch:
        print("Continuing to fetch images...")
        interactive_game_image("")
    return 0
