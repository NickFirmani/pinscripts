#!/usr/bin/env python3

"""Command-line interface for the pinball commentary binder tools."""

import argparse
import sys
from pathlib import Path

from pinscripts.ai import interactive_game_format, interactive_research_prompt, print_format_prompt
from pinscripts.binder_workflows import (
    add_binder_game,
    create_binder_interactive,
    edit_venue_notes,
    mark_binder_printed,
    remove_binder_game,
    show_binder_status,
    sync_binder_interactive,
)
from pinscripts.build import (
    BuildInputError,
    build_binder,
    build_catalog,
    build_game,
    build_print_packet,
    validate_project,
)
from pinscripts.game_workflows import interactive_add_game, interactive_update_game
from pinscripts.images import (
    interactive_black_and_white_images,
    interactive_game_image,
    interactive_low_resolution_image_repair,
)
from pinscripts.shot_labels import interactive_shot_labels
from scripts.process_images import process_images


def _add_color_mode(parser):
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--color", dest="black_and_white", action="store_false")
    modes.add_argument("--black-and-white", "--bw", dest="black_and_white", action="store_true")
    parser.set_defaults(black_and_white=False)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Manage a location-neutral pinball catalog and physical binder manifests."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    catalog = commands.add_parser("catalog", help="Build the master catalog PDF")
    catalog_commands = catalog.add_subparsers(dest="catalog_command", required=True)
    catalog_build = catalog_commands.add_parser("build")
    _add_color_mode(catalog_build)

    game = commands.add_parser("game", help="Create, update, or render catalog content")
    game_commands = game.add_subparsers(dest="game_command", required=True)
    game_build = game_commands.add_parser("build")
    game_build.add_argument("game_id")
    game_build.add_argument("--binder", dest="binder_id")
    _add_color_mode(game_build)
    game_add = game_commands.add_parser("add")
    game_add.add_argument("description", nargs="?", default="")
    game_add.add_argument("--binder", dest="binder_id")
    game_update = game_commands.add_parser("update")
    game_update.add_argument("game", nargs="?", default="")
    game_research = game_commands.add_parser("research")
    game_research.add_argument("description", nargs="?", default="")
    game_format = game_commands.add_parser("format")
    game_format.add_argument("research_id", nargs="?", default="")
    game_image = game_commands.add_parser("image")
    game_image.add_argument("game", nargs="?", default="")
    game_image_bw = game_commands.add_parser("image-bw")
    game_image_bw.add_argument("game", nargs="?", default="")
    game_image_low = game_commands.add_parser("image-low-res")
    game_image_low.add_argument("game", nargs="?", default="")

    binder = commands.add_parser("binder", help="Manage physical binder manifests")
    binder_commands = binder.add_subparsers(dest="binder_command", required=True)
    binder_create = binder_commands.add_parser("create")
    binder_create.add_argument("binder_id")
    binder_create.add_argument("--title")
    create_source = binder_create.add_mutually_exclusive_group(required=True)
    create_source.add_argument("--games-file", type=Path)
    create_source.add_argument("--pinball-map")
    create_source.add_argument("--paste", action="store_true")
    binder_sync = binder_commands.add_parser("sync")
    binder_sync.add_argument("binder_id")
    sync_source = binder_sync.add_mutually_exclusive_group()
    sync_source.add_argument("--pinball-map")
    sync_source.add_argument("--paste", action="store_true")
    binder_build = binder_commands.add_parser("build")
    binder_build.add_argument("binder_id")
    _add_color_mode(binder_build)
    binder_add = binder_commands.add_parser("add-game")
    binder_add.add_argument("binder_id")
    binder_add.add_argument("game")
    binder_remove = binder_commands.add_parser("remove-game")
    binder_remove.add_argument("binder_id")
    binder_remove.add_argument("game")
    binder_notes = binder_commands.add_parser("notes")
    binder_notes.add_argument("binder_id")
    binder_notes.add_argument("game")
    binder_printed = binder_commands.add_parser("mark-printed")
    binder_printed.add_argument("binder_id")
    binder_printed.add_argument("--date", dest="printed_at")
    binder_packet = binder_commands.add_parser("packet")
    binder_packet.add_argument("binder_id")
    binder_packet.add_argument("game_id")
    binder_packet.add_argument("--operation", choices=("add", "update"), default="update")
    _add_color_mode(binder_packet)
    binder_commands.add_parser("status").add_argument("binder_id")

    shot_labels = commands.add_parser("shot-labels")
    shot_labels.add_argument("game", nargs="?", default="")

    validation = commands.add_parser("validate")

    image_process = commands.add_parser("process-images")
    image_process.add_argument("source", type=Path)
    image_process.add_argument("--output-dir", type=Path)

    format_prompt = commands.add_parser("format-prompt")
    format_prompt.add_argument("research")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "catalog":
            return build_catalog(args.black_and_white)
        if args.command == "validate":
            return validate_project()
        if args.command == "shot-labels":
            return interactive_shot_labels(args.game)
        if args.command == "process-images":
            process_images(args.source, args.output_dir)
            return 0
        if args.command == "format-prompt":
            return print_format_prompt(args.research)
        if args.command == "game":
            if args.game_command == "build":
                return build_game(args.game_id, args.black_and_white, args.binder_id)
            if args.game_command == "add":
                return interactive_add_game(args.description, args.binder_id)
            if args.game_command == "update":
                return interactive_update_game(args.game)
            if args.game_command == "research":
                return interactive_research_prompt(args.description)
            if args.game_command == "format":
                return interactive_game_format(args.research_id)
            if args.game_command == "image":
                return interactive_game_image(args.game)
            if args.game_command == "image-bw":
                return interactive_black_and_white_images(args.game)
            if args.game_command == "image-low-res":
                return interactive_low_resolution_image_repair(args.game)
        if args.command == "binder":
            if args.binder_command == "create":
                return create_binder_interactive(
                    args.binder_id,
                    args.title,
                    games_file=args.games_file,
                    pinball_map=args.pinball_map,
                    paste=args.paste,
                )
            if args.binder_command == "sync":
                return sync_binder_interactive(
                    args.binder_id,
                    pinball_map=args.pinball_map,
                    paste=args.paste,
                )
            if args.binder_command == "build":
                return build_binder(args.binder_id, args.black_and_white)
            if args.binder_command == "add-game":
                return add_binder_game(args.binder_id, args.game)
            if args.binder_command == "remove-game":
                return remove_binder_game(args.binder_id, args.game)
            if args.binder_command == "notes":
                return edit_venue_notes(args.binder_id, args.game)
            if args.binder_command == "mark-printed":
                return mark_binder_printed(args.binder_id, args.printed_at)
            if args.binder_command == "packet":
                packet = build_print_packet(
                    args.game_id,
                    args.operation,
                    args.binder_id,
                    args.black_and_white,
                )
                print(f"Wrote {packet}")
                return 0
            if args.binder_command == "status":
                return show_binder_status(args.binder_id)
    except (BuildInputError, OSError, ValueError) as error:
        parser.error(str(error))
    parser.error("unknown command")


if __name__ == "__main__":
    sys.exit(main())
