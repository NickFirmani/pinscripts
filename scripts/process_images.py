#!/usr/bin/env python3

import argparse
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


VARIANTS = {
    "gray": [
        "-auto-orient",
        "-resize", "300%",
        "-filter", "Lanczos",
        "-colorspace", "Gray",
        "-contrast-stretch", "0.5%x0.5%",
        "-clahe", "8x8+128+3",
        "-unsharp", "0x1.5+1.2+0.02",
    ],

    "gray-soft": [
        "-auto-orient",
        "-resize", "300%",
        "-filter", "Lanczos",
        "-colorspace", "Gray",
        "-contrast-stretch", "0.2%x0.2%",
        "-unsharp", "0x1.0+0.8+0.02",
    ],

    "posterize-4": [
        "-auto-orient",
        "-resize", "300%",
        "-filter", "Lanczos",
        "-colorspace", "Gray",
        "-contrast-stretch", "0.5%x0.5%",
        "-clahe", "8x8+128+3",
        "-unsharp", "0x1.2+1.0+0.02",
        "-posterize", "4",
    ],

    "posterize-6": [
        "-auto-orient",
        "-resize", "300%",
        "-filter", "Lanczos",
        "-colorspace", "Gray",
        "-contrast-stretch", "0.5%x0.5%",
        "-clahe", "8x8+128+3",
        "-unsharp", "0x1.2+1.0+0.02",
        "-posterize", "6",
    ],
}


# ImageMagick does the CPU-heavy work in child processes, so threads let several
# independent variants run at once without adding multiprocessing overhead here.
# Keep the pool modest: the 300% resize can make each conversion memory-hungry.
MAX_PARALLEL_VARIANTS = 4
WEBP_OUTPUT_ARGS = ["-define", "webp:lossless=true"]


def require_imagemagick() -> str:
    magick = shutil.which("magick")

    if magick is None:
        raise SystemExit(
            "ImageMagick is required to process images, but the `magick` "
            "command was not found. Install ImageMagick and ensure `magick` "
            "is available on PATH."
        )

    return magick


def run_variant(
    source: Path,
    output: Path,
    args: list[str],
    magick: str = "magick",
    show_progress: bool = True,
) -> None:
    cmd = [
        magick,
        str(source),
        *args,
        *WEBP_OUTPUT_ARGS,
        str(output),
    ]

    if show_progress:
        print(f"→ {output.name}")
    subprocess.run(cmd, check=True)


def process_images(
    source: Path,
    output_dir: Path | None = None,
    show_progress: bool = True,
) -> Path:
    source = source.resolve()

    if not source.exists():
        raise SystemExit(f"Source image does not exist: {source}")

    magick = require_imagemagick()

    if output_dir is None:
        output_dir = source.parent / f"{source.stem}-variants"

    output_dir.mkdir(parents=True, exist_ok=True)

    jobs = [
        (
            source,
            output_dir / f"{source.stem}-{name}.webp",
            variant_args,
            magick,
            show_progress,
        )
        for name, variant_args in VARIANTS.items()
    ]
    worker_count = min(MAX_PARALLEL_VARIANTS, len(jobs))
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = [executor.submit(run_variant, *job) for job in jobs]
        for future in futures:
            future.result()

    if show_progress:
        print()
        print(f"Generated {len(VARIANTS)} variants in:")
        print(output_dir)

    return output_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate B/W and grayscale print variants of a playfield image."
    )

    parser.add_argument(
        "source",
        type=Path,
        help="Source image",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: <source>-variants)",
    )

    args = parser.parse_args()

    process_images(args.source, args.output_dir)


if __name__ == "__main__":
    main()
