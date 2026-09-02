import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import yaml

import main as app


class VenueNotesReviewTests(unittest.TestCase):
    def make_game(self, directory, name="example-game.yaml"):
        path = Path(directory) / name
        path.write_text(
            "id: example-game\n"
            "name: Example Game\n"
            "hook: >-\n"
            "  Preserve this formatting exactly.\n"
            "venue_notes:\n"
            "- Keep this note.\n"
            "- Remove this note.\n"
            "- Edit this note.\n"
            "image: images/example-game.jpg\n",
            encoding="utf-8",
        )
        return path

    def test_review_accepts_removes_and_edits_notes(self):
        with tempfile.TemporaryDirectory() as directory:
            content = Path(directory)
            path = self.make_game(content)
            with (
                patch.object(app, "CONTENT", content),
                patch(
                    "builtins.input",
                    side_effect=["", "r", "e", "Edited replacement."],
                ),
                redirect_stdout(io.StringIO()),
            ):
                result = app.interactive_review_venue_notes("")

            updated_text = path.read_text(encoding="utf-8")
            updated = yaml.safe_load(updated_text)

        self.assertEqual(result, 0)
        self.assertEqual(
            updated["venue_notes"],
            ["Keep this note.", "Edited replacement."],
        )
        self.assertIn("hook: >-\n  Preserve this formatting exactly.\n", updated_text)

    def test_quit_saves_prior_decisions_and_preserves_remaining_notes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.make_game(directory)
            with (
                patch("builtins.input", side_effect=["r", "q"]),
                redirect_stdout(io.StringIO()),
            ):
                result = app.interactive_review_venue_notes(str(path))

            updated = yaml.safe_load(path.read_text(encoding="utf-8"))

        self.assertEqual(result, 0)
        self.assertEqual(
            updated["venue_notes"],
            ["Remove this note.", "Edit this note."],
        )

    def test_missing_requested_game_returns_error(self):
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(app, "CONTENT", Path(directory)),
                redirect_stderr(stderr),
            ):
                result = app.interactive_review_venue_notes("missing-game")

        self.assertEqual(result, 1)
        self.assertIn("no content file", stderr.getvalue())

    def test_main_dispatches_venue_notes_review(self):
        with (
            patch.object(
                app,
                "interactive_review_venue_notes",
                return_value=0,
            ) as review,
            patch(
                "sys.argv",
                ["main.py", "--review-venue-notes", "example-game"],
            ),
        ):
            result = app.main()

        self.assertEqual(result, 0)
        review.assert_called_once_with("example-game")


if __name__ == "__main__":
    unittest.main()
