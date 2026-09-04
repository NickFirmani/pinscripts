import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main as cli
import pinscripts.build as app
from pinscripts.manual import Manual, ManualEntry


class BuildTests(unittest.TestCase):
    def test_render_names_bw_output_and_passes_mode_to_renderer(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            content_path = Path("content/example-game.yaml")

            with (
                patch.object(app, "OUTPUT", output),
                patch.object(app, "render_game") as render_game,
            ):
                app.render([content_path], black_and_white=True)

        render_game.assert_called_once_with(
            content_path,
            output / "example-game-bw.pdf",
            True,
        )

    def test_parser_defaults_to_color_and_accepts_both_modes(self):
        parser = cli.build_parser()

        self.assertFalse(parser.parse_args(["example-game"]).black_and_white)
        self.assertFalse(
            parser.parse_args(["example-game", "--color"]).black_and_white
        )
        self.assertTrue(parser.parse_args(["example-game", "--bw"]).black_and_white)

    def test_all_bw_uses_manual_order_and_builds_the_binder(self):
        content_path = app.CONTENT / "example-game.yaml"
        output = Path("/project/output")
        manual = Manual(
            1,
            (ManualEntry("example-game", ("2", "3")),),
        )

        with (
            patch.object(app, "OUTPUT", output),
            patch.object(app, "load_manual", return_value=manual),
            patch.object(app, "validate_all", return_value=True),
            patch.object(app, "render") as render,
            patch.object(app, "merge_pdfs") as merge_pdfs,
        ):
            result = app.build_all(True)

        self.assertEqual(result, 0)
        render.assert_called_once_with(
            [content_path],
            True,
            True,
            {"example-game": ("2", "3")},
        )
        merge_pdfs.assert_called_once_with(
            [output / "example-game-bw.pdf"],
            output / "binder-bw.pdf",
        )

    def test_main_dispatches_full_build(self):
        with patch.object(cli, "build_all", return_value=0) as build:
            result = cli.main(["--all", "--bw"])

        self.assertEqual(result, 0)
        build.assert_called_once_with(True)

    def test_main_dispatches_add_and_update_workflows(self):
        with patch.object(cli, "interactive_add_game", return_value=0) as add:
            self.assertEqual(cli.main(["--add", "New Game 2026"]), 0)
        add.assert_called_once_with("New Game 2026")

        with patch.object(cli, "interactive_update_game", return_value=0) as update:
            self.assertEqual(cli.main(["--update", "example-game", "--bw"]), 0)
        update.assert_called_once_with("example-game")

    def test_print_packet_renders_every_game_with_its_permanent_labels(self):
        manual = Manual(
            1,
            (
                ManualEntry("alpha", ("18", "19")),
                ManualEntry("bravo", ("19.1", "19.2")),
                ManualEntry("charlie", ("20", "21")),
            ),
        )
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            with (
                patch.object(app, "OUTPUT", output),
                patch.object(app, "validate_all", return_value=True),
                patch.object(app, "render_game") as render_game,
                patch.object(app, "merge_print_packet") as merge_packet,
            ):
                result = app.build_print_packet("bravo", "add", manual)

        self.assertEqual(result, output / "print" / "add-bravo.pdf")
        self.assertEqual(
            [call.kwargs["page_labels"] for call in render_game.call_args_list],
            [("18", "19"), ("19.1", "19.2"), ("20", "21")],
        )
        merge_packet.assert_called_once()


if __name__ == "__main__":
    unittest.main()
