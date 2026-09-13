import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pinscripts.game_workflows as app
from pinscripts.binder import Binder, BinderEntry, BinderSource


class GameWorkflowTests(unittest.TestCase):
    def test_add_lock_rejects_a_parallel_claim_for_the_same_game(self):
        with tempfile.TemporaryDirectory() as directory:
            locks = Path(directory)
            with app._claim_add_game("alpha", locks) as first:
                with app._claim_add_game("alpha", locks) as second:
                    self.assertTrue(first)
                    self.assertFalse(second)

    def test_print_mode_defaults_to_color(self):
        with patch("builtins.input", return_value=""):
            self.assertFalse(app.request_print_mode())

    def test_add_is_catalog_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = root / "content"
            content.mkdir()

            def make_content(_description, research_id=None):
                (content / f"{research_id}.yaml").write_text("id: bravo\n", encoding="utf-8")
                return 0

            with (
                patch.object(app, "CONTENT", content),
                patch.object(app, "ROOT", root),
                patch.object(app, "OUTPUT", root / "output"),
                patch.object(app, "RESEARCH", content / "research"),
                patch.object(app, "_request_new_identity", return_value=("Bravo", "bravo")),
                patch.object(app, "ask_yes_no", return_value=True),
                patch.object(app, "interactive_research_prompt", side_effect=make_content),
                patch.object(app, "_ensure_game_assets", return_value=True),
                patch.object(app, "validate_all", return_value=True),
            ):
                result = app.interactive_add_game("Bravo")

        self.assertEqual(result, 0)

    def test_add_resumes_when_catalog_content_already_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = root / "content"
            content.mkdir()
            (content / "bravo.yaml").write_text(
                "id: bravo\nname: Bravo\nimage: images/bravo.webp\n",
                encoding="utf-8",
            )
            with (
                patch.object(app, "CONTENT", content),
                patch.object(app, "ROOT", root),
                patch.object(app, "OUTPUT", root / "output"),
                patch.object(
                    app,
                    "_request_new_identity",
                    return_value=("Bravo", "bravo"),
                ),
                patch.object(app, "interactive_research_prompt") as research,
                patch.object(app, "_ensure_game_assets", return_value=True),
                patch.object(app, "validate_all", return_value=True),
            ):
                first = app.interactive_add_game("Bravo")
                second = app.interactive_add_game("Bravo")

        self.assertEqual((first, second), (0, 0))
        research.assert_not_called()

    def test_asset_check_skips_current_shot_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = root / "content"
            images = root / "images"
            content.mkdir()
            images.mkdir()
            (content / "alpha.yaml").write_text(
                "id: alpha\nimage: images/alpha.webp\n",
                encoding="utf-8",
            )
            (images / "alpha.webp").touch()
            with (
                patch.object(app, "CONTENT", content),
                patch.object(app, "ROOT", root),
                patch.object(app, "shot_label_issue", return_value=None),
                patch.object(app, "ask_yes_no") as ask,
                patch.object(app, "interactive_shot_labels") as labels,
            ):
                ready = app._ensure_game_assets(
                    "Alpha",
                    "alpha",
                    False,
                    offer_shot_labels=True,
                )

        self.assertTrue(ready)
        ask.assert_not_called()
        labels.assert_not_called()

    def test_update_builds_a_packet_for_every_printed_binder(self):
        printed = Binder(
            1,
            "printed",
            "Printed",
            "printed",
            None,
            BinderSource("manual"),
            (BinderEntry("alpha", ("2", "3")),),
        )
        draft = Binder(
            1,
            "draft",
            "Draft",
            "draft",
            None,
            BinderSource("manual"),
            (BinderEntry("alpha", ("2", "3")),),
        )
        with tempfile.TemporaryDirectory() as directory:
            content = Path(directory)
            (content / "alpha.yaml").write_text(
                "id: alpha\nname: Alpha\nmetadata: {}\nimage: images/alpha.webp\n",
                encoding="utf-8",
            )
            with (
                patch.object(app, "CONTENT", content),
                patch.object(app, "_request_game_id", return_value="alpha"),
                patch("builtins.input", return_value="4"),
                patch.object(app, "validate_game_contexts", return_value=True),
                patch.object(app, "binders_containing", return_value=[printed, draft]),
                patch.object(app, "ask_yes_no", return_value=True),
                patch.object(app, "request_print_mode", return_value=False),
                patch.object(app, "_ensure_game_assets", return_value=True),
                patch.object(
                    app,
                    "build_print_packet",
                    return_value=app.ROOT / "packet.pdf",
                ) as packet,
            ):
                result = app.interactive_update_game("alpha")

        self.assertEqual(result, 0)
        packet.assert_called_once_with("alpha", "update", printed, False)


if __name__ == "__main__":
    unittest.main()
