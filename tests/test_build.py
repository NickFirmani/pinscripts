import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main as cli
import pinscripts.build as app


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

    def test_bw_binder_uses_bw_individual_and_binder_names(self):
        content_path = Path("content/example-game.yaml")
        output = Path("/project/output")

        with (
            patch.object(app, "OUTPUT", output),
            patch.object(
                app,
                "content_for_selected_pins",
                return_value=[content_path],
            ),
            patch.object(app, "validate_all", return_value=True),
            patch.object(app, "render") as render,
            patch.object(app, "merge_pdfs") as merge_pdfs,
        ):
            result = app.build_selected(True, binder=True)

        self.assertEqual(result, 0)
        render.assert_called_once_with([content_path], True)
        merge_pdfs.assert_called_once_with(
            [output / "example-game-bw.pdf"],
            output / "binder-bw.pdf",
        )

    def test_main_dispatches_binder_build(self):
        with patch.object(cli, "build_selected", return_value=0) as build:
            result = cli.main(["--binder", "--bw"])

        self.assertEqual(result, 0)
        build.assert_called_once_with(True, binder=True)


if __name__ == "__main__":
    unittest.main()
