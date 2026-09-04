#!/usr/bin/env python3

"""Command-line interface for the pinball commentary binder tools."""

import argparse
import sys
from pathlib import Path

from pinscripts.ai import (
    interactive_game_format,
    interactive_research_prompt,
    print_format_prompt,
)
from pinscripts.build import BuildInputError, build_all, build_game
from pinscripts.images import (
    interactive_black_and_white_images,
    interactive_game_image,
    interactive_low_resolution_image_repair,
)
from pinscripts.game_workflows import interactive_add_game, interactive_update_game
from pinscripts.shot_labels import interactive_shot_labels
from pinscripts.venue_notes import interactive_review_venue_notes
from scripts.process_images import process_images


def build_parser():
    parser = argparse.ArgumentParser(
        description="Validate and render pinball commentary sheets.",
    )
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument(
        "game",
        nargs="?",
        help="Game ID, e.g. playboy-bally-1978",
    )
    actions.add_argument(
        "--all",
        action="store_true",
        help="Render every game in manual.yaml and create binder.pdf",
    )
    actions.add_argument(
        "--add",
        nargs="?",
        const="",
        metavar="DESCRIPTION",
        help="Interactively add a game to the printed manual",
    )
    actions.add_argument(
        "--update",
        nargs="?",
        const="",
        metavar="GAME",
        help="Interactively update a game and build a replacement packet",
    )
    actions.add_argument(
        "--game-research",
        nargs="?",
        const="",
        metavar="DESCRIPTION",
        help="Print a research prompt, prompting for the description if omitted",
    )
    actions.add_argument(
        "--game-format",
        nargs="?",
        const="",
        metavar="RESEARCH_ID",
        help="Format an existing content/research/<id>.md brief",
    )
    actions.add_argument(
        "--game-image",
        nargs="?",
        const="",
        metavar="NAME",
        help="Open a Google Image search and copy the newest download",
    )
    actions.add_argument(
        "--game-image-bw",
        nargs="?",
        const="",
        metavar="NAME",
        help="Generate and choose a black-and-white image variant",
    )
    actions.add_argument(
        "--game-image-low-res",
        nargs="?",
        const="",
        metavar="NAME",
        help="Replace low-resolution images using Google Image search",
    )
    actions.add_argument(
        "--shot-labels",
        nargs="?",
        const="",
        metavar="GAME",
        help="Place numbered shot markers on a game's playfield image",
    )
    actions.add_argument(
        "--review-venue-notes",
        nargs="?",
        const="",
        metavar="GAME",
        help="Accept, remove, or edit Venue Notes one at a time",
    )
    actions.add_argument(
        "--format-prompt",
        metavar="RESEARCH",
        help="Print the phase-two YAML prompt using a research file, or - for stdin",
    )
    actions.add_argument(
        "--process-images",
        metavar="SOURCE",
        type=Path,
        help="Generate print variants of a playfield image",
    )
    parser.add_argument(
        "--image-output-dir",
        metavar="DIRECTORY",
        type=Path,
        help="Output directory for --process-images",
    )
    image_modes = parser.add_mutually_exclusive_group()
    image_modes.add_argument(
        "--color",
        dest="black_and_white",
        action="store_false",
        help="Use the image named in the game YAML (default)",
    )
    image_modes.add_argument(
        "--black-and-white",
        "--bw",
        dest="black_and_white",
        action="store_true",
        help="Use the image with -bw appended before its extension",
    )
    parser.set_defaults(black_and_white=False)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.add is not None:
        return interactive_add_game(args.add)
    if args.update is not None:
        return interactive_update_game(args.update)
    if args.game_research is not None:
        return interactive_research_prompt(args.game_research)
    if args.game_format is not None:
        return interactive_game_format(args.game_format)
    if args.game_image is not None:
        return interactive_game_image(args.game_image)
    if args.game_image_bw is not None:
        return interactive_black_and_white_images(args.game_image_bw)
    if args.game_image_low_res is not None:
        return interactive_low_resolution_image_repair(args.game_image_low_res)
    if args.shot_labels is not None:
        return interactive_shot_labels(args.shot_labels)
    if args.review_venue_notes is not None:
        return interactive_review_venue_notes(args.review_venue_notes)
    if args.format_prompt:
        try:
            return print_format_prompt(args.format_prompt)
        except OSError as error:
            parser.error(f"could not read research brief: {error}")
    if args.process_images:
        process_images(args.process_images, args.image_output_dir)
        return 0
    if args.image_output_dir:
        parser.error("--image-output-dir requires --process-images")
    if args.game:
        try:
            return build_game(args.game, args.black_and_white)
        except BuildInputError as error:
            parser.error(str(error))
    if args.all:
        return build_all(args.black_and_white)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
