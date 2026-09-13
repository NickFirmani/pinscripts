import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pinscripts.game_workflows as app
from pinscripts.binder import Binder, BinderEntry, BinderSource


class GameWorkflowTests(unittest.TestCase):
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
                patch.object(app, "RESEARCH", content / "research"),
                patch.object(app, "_request_new_identity", return_value=("Bravo", "bravo")),
                patch.object(app, "ask_yes_no", return_value=True),
                patch.object(app, "interactive_research_prompt", side_effect=make_content),
                patch.object(app, "_ensure_game_assets", return_value=True),
                patch.object(app, "validate_all", return_value=True),
            ):
                result = app.interactive_add_game("Bravo")

        self.assertEqual(result, 0)

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
