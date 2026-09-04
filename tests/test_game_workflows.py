import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pinscripts.game_workflows as app
from pinscripts.build import BuildInputError
from pinscripts.manual import Manual, ManualEntry


class GameWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.manual = Manual(
            1,
            (ManualEntry("alpha", ("2", "3")),),
        )

    def test_print_mode_defaults_to_color(self):
        with patch("builtins.input", return_value=""):
            self.assertFalse(app.request_print_mode())

    def test_print_mode_accepts_black_and_white_after_invalid_answer(self):
        with patch("builtins.input", side_effect=["sepia", "bw"]):
            self.assertTrue(app.request_print_mode())

    def test_print_mode_cancels_when_input_closes(self):
        with patch("builtins.input", side_effect=EOFError):
            self.assertIsNone(app.request_print_mode())

    def test_add_resumes_an_existing_research_brief(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = root / "content"
            research = content / "research"
            research.mkdir(parents=True)
            (research / "bravo.md").write_text("research", encoding="utf-8")

            def format_existing(game_id):
                (content / f"{game_id}.yaml").write_text("id: bravo\n", encoding="utf-8")
                return 0

            with (
                patch.object(app, "CONTENT", content),
                patch.object(app, "RESEARCH", research),
                patch.object(app, "ROOT", root),
                patch.object(app, "load_manual", return_value=self.manual),
                patch.object(app, "_request_new_identity", return_value=("Bravo", "bravo")),
                patch.object(app, "_choose_insertion_index", return_value=1),
                patch.object(app, "ask_yes_no", return_value=True),
                patch.object(app, "request_print_mode", return_value=False),
                patch.object(app, "interactive_game_format", side_effect=format_existing) as formatter,
                patch.object(app, "_ensure_game_assets", return_value=True) as assets,
                patch.object(app, "validate_all", return_value=True),
                patch.object(
                    app,
                    "build_print_packet",
                    return_value=root / "packet.pdf",
                ) as build_packet,
                patch.object(app, "write_manual") as write_manual,
            ):
                result = app.interactive_add_game("Bravo")

        self.assertEqual(result, 0)
        formatter.assert_called_once_with("bravo")
        assets.assert_called_once_with(
            "Bravo",
            "bravo",
            True,
            offer_shot_labels=True,
        )
        build_packet.assert_called_once_with("bravo", "add", unittest.mock.ANY, False)
        write_manual.assert_called_once()

    def test_asset_setup_places_labels_before_generating_black_and_white(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = root / "content"
            images = root / "images"
            content.mkdir()
            images.mkdir()
            (content / "bravo.yaml").write_text(
                "image: images/bravo.webp\n",
                encoding="utf-8",
            )
            (images / "bravo.webp").touch()
            events = []

            def label(*_args, **_kwargs):
                events.append("labels")
                return 0

            def make_black_and_white(_game_id):
                events.append("black-and-white")
                (images / "bravo-bw.webp").touch()
                return 0

            with (
                patch.object(app, "CONTENT", content),
                patch.object(app, "ROOT", root),
                patch.object(app, "ask_yes_no", return_value=True),
                patch.object(app, "interactive_shot_labels", side_effect=label),
                patch.object(
                    app,
                    "interactive_black_and_white_images",
                    side_effect=make_black_and_white,
                ),
            ):
                result = app._ensure_game_assets(
                    "Bravo",
                    "bravo",
                    True,
                    offer_shot_labels=True,
                )

        self.assertTrue(result)
        self.assertEqual(events, ["labels", "black-and-white"])

    def test_add_keeps_saved_manifest_when_packet_build_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = root / "content"
            content.mkdir()
            (content / "bravo.yaml").write_text("id: bravo\n", encoding="utf-8")

            with (
                patch.object(app, "CONTENT", content),
                patch.object(app, "ROOT", root),
                patch.object(app, "load_manual", return_value=self.manual),
                patch.object(app, "_request_new_identity", return_value=("Bravo", "bravo")),
                patch.object(app, "_choose_insertion_index", return_value=1),
                patch.object(app, "ask_yes_no", return_value=True),
                patch.object(app, "request_print_mode", return_value=False),
                patch.object(app, "_ensure_game_assets", return_value=True),
                patch.object(app, "validate_all", return_value=True),
                patch.object(
                    app,
                    "build_print_packet",
                    side_effect=BuildInputError("render failed"),
                ),
                patch.object(app, "write_manual") as write_manual,
            ):
                result = app.interactive_add_game("Bravo")

        self.assertEqual(result, 1)
        write_manual.assert_called_once()

    def test_add_can_save_manifest_without_generating_a_packet(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = root / "content"
            content.mkdir()
            (content / "bravo.yaml").write_text("id: bravo\n", encoding="utf-8")

            with (
                patch.object(app, "CONTENT", content),
                patch.object(app, "ROOT", root),
                patch.object(app, "load_manual", return_value=self.manual),
                patch.object(app, "_request_new_identity", return_value=("Bravo", "bravo")),
                patch.object(app, "_choose_insertion_index", return_value=1),
                patch.object(app, "ask_yes_no", side_effect=[True, False]),
                patch.object(app, "_ensure_game_assets", return_value=True),
                patch.object(app, "validate_all", return_value=True),
                patch.object(app, "request_print_mode") as mode,
                patch.object(app, "build_print_packet") as build_packet,
                patch.object(app, "write_manual") as write_manual,
            ):
                result = app.interactive_add_game("Bravo")

        self.assertEqual(result, 0)
        write_manual.assert_called_once()
        mode.assert_not_called()
        build_packet.assert_not_called()

    def test_update_chooses_black_and_white_only_before_packet_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = root / "content"
            content.mkdir()
            (content / "alpha.yaml").write_text(
                "id: alpha\nname: Alpha\nimage: images/alpha.webp\nmetadata: {}\n",
                encoding="utf-8",
            )

            with (
                patch.object(app, "CONTENT", content),
                patch.object(app, "ROOT", root),
                patch.object(app, "load_manual", return_value=self.manual),
                patch("builtins.input", return_value="5"),
                patch.object(app, "ask_yes_no", return_value=True),
                patch.object(app, "request_print_mode", return_value=True) as mode,
                patch.object(app, "_ensure_game_assets", return_value=True) as assets,
                patch.object(app, "validate_all", return_value=True),
                patch.object(
                    app,
                    "build_print_packet",
                    return_value=root / "packet.pdf",
                ) as build_packet,
            ):
                result = app.interactive_update_game("alpha")

        self.assertEqual(result, 0)
        mode.assert_called_once_with()
        assets.assert_called_once_with(
            "Alpha",
            "alpha",
            True,
            rebuild_black_and_white=False,
        )
        build_packet.assert_called_once_with("alpha", "update", self.manual, True)

    def test_update_rebuilds_black_and_white_after_replacing_and_relabeling(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = root / "content"
            content.mkdir()
            (content / "alpha.yaml").write_text(
                "id: alpha\nname: Alpha\nimage: images/alpha.webp\nmetadata: {}\n",
                encoding="utf-8",
            )
            events = []

            with (
                patch.object(app, "CONTENT", content),
                patch.object(app, "ROOT", root),
                patch.object(app, "load_manual", return_value=self.manual),
                patch("builtins.input", return_value="2"),
                patch.object(app, "ask_yes_no", return_value=True),
                patch.object(app, "interactive_game_image", return_value=0),
                patch.object(
                    app,
                    "interactive_shot_labels",
                    side_effect=lambda *_args, **_kwargs: events.append("labels") or 0,
                ),
                patch.object(
                    app,
                    "_ensure_game_assets",
                    side_effect=lambda *_args, **_kwargs: events.append("assets") or True,
                ) as assets,
                patch.object(app, "validate_all", return_value=True),
                patch.object(app, "request_print_mode", return_value=False),
                patch.object(
                    app,
                    "build_print_packet",
                    return_value=root / "packet.pdf",
                ),
            ):
                result = app.interactive_update_game("alpha")

        self.assertEqual(result, 0)
        self.assertEqual(events[:2], ["labels", "assets"])
        self.assertEqual(
            assets.call_args_list[0],
            unittest.mock.call(
                "Alpha",
                "alpha",
                True,
                rebuild_black_and_white=True,
            ),
        )

    def test_rejected_content_candidate_leaves_original_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = root / "content"
            content.mkdir()
            original_path = content / "alpha.yaml"
            original_path.write_text("id: alpha\nname: Old\n", encoding="utf-8")

            def write_candidate(_description, research_id=None, formatted_output_path=None):
                self.assertEqual(research_id, "alpha")
                formatted_output_path.write_text(
                    "id: alpha\nname: New\n",
                    encoding="utf-8",
                )
                return 0

            with (
                patch.object(app, "CONTENT", content),
                patch.object(app, "ROOT", root),
                patch.object(app, "interactive_research_prompt", side_effect=write_candidate),
                patch.object(app, "ask_yes_no", return_value=False),
            ):
                accepted = app._refresh_content_with_review("alpha", "Alpha")

            unchanged = original_path.read_text(encoding="utf-8")

        self.assertFalse(accepted)
        self.assertEqual(unchanged, "id: alpha\nname: Old\n")


if __name__ == "__main__":
    unittest.main()
