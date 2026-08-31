import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import main as app
from scripts import render as renderer


class RenderTests(unittest.TestCase):
    def story_text(self, data):
        return [
            item.getPlainText()
            for item in renderer.build_story(data)
            if hasattr(item, "getPlainText")
        ]

    def test_empty_skill_shots_and_features_do_not_render_sections(self):
        data = app.load_yaml(app.CONTENT / "playboy-bally-1978.yaml")

        text = self.story_text(data)

        self.assertNotIn("SKILL SHOTS", text)
        self.assertNotIn("SPECIAL FEATURES", text)

    def test_skill_shots_and_features_render_conditionally(self):
        data = deepcopy(app.load_yaml(app.CONTENT / "playboy-bally-1978.yaml"))
        data["skill_shots"] = [
            {
                "name": "Super Skill Shot",
                "how": "Hold the left flipper and plunge the flashing lane.",
                "value": "Awards immediate progression.",
            }
        ]
        data["features"] = [
            {
                "type": "video-mode",
                "name": "Video Mode",
                "text": "Use the flipper buttons to complete the display objective.",
            }
        ]

        text = self.story_text(data)

        self.assertIn("SKILL SHOTS", text)
        self.assertTrue(any("Super Skill Shot" in item for item in text))
        self.assertIn("SPECIAL FEATURES", text)
        self.assertTrue(any("Video Mode" in item for item in text))

    def test_color_uses_configured_image_path(self):
        with patch.object(renderer, "ROOT", Path("/project")):
            result = renderer.resolve_image_path(
                "images/example-game.png",
                black_and_white=False,
            )

        self.assertEqual(result, Path("/project/images/example-game.png"))

    def test_black_and_white_uses_bw_suffix_before_extension(self):
        with patch.object(renderer, "ROOT", Path("/project")):
            result = renderer.resolve_image_path(
                "images/example-game.png",
                black_and_white=True,
            )

        self.assertEqual(result, Path("/project/images/example-game-bw.png"))

    def test_black_and_white_does_not_duplicate_existing_suffix(self):
        with patch.object(renderer, "ROOT", Path("/project")):
            result = renderer.resolve_image_path(
                "images/example-game-bw.png",
                black_and_white=True,
            )

        self.assertEqual(result, Path("/project/images/example-game-bw.png"))

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
        parser = app.build_parser()

        self.assertFalse(parser.parse_args(["example-game"]).black_and_white)
        self.assertFalse(
            parser.parse_args(["example-game", "--color"]).black_and_white
        )
        self.assertTrue(
            parser.parse_args(["example-game", "--bw"]).black_and_white
        )

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
            patch("sys.argv", ["main.py", "--binder", "--bw"]),
        ):
            result = app.main()

        self.assertEqual(result, 0)
        render.assert_called_once_with([content_path], True)
        merge_pdfs.assert_called_once_with(
            [output / "example-game-bw.pdf"],
            output / "binder-bw.pdf",
        )


if __name__ == "__main__":
    unittest.main()
