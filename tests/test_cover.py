import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pypdf import PdfReader

import main as cli
import pinscripts.build as build
from pinscripts.binder import Binder, BinderEntry, BinderSource
from pinscripts.cover import BinderCoverError, ask_spine_width, parse_spine_width, render_binder_inserts


class BinderCoverTests(unittest.TestCase):
    def test_spine_width_accepts_decimals_units_and_mixed_fractions(self):
        self.assertEqual(parse_spine_width("1.5 inches"), 1.5)
        self.assertEqual(parse_spine_width('2"'), 2.0)
        self.assertEqual(parse_spine_width("1 1/2"), 1.5)

    def test_spine_width_rejects_sizes_that_do_not_fit_letter_paper(self):
        for value in ("", "wide", 0.25, 6):
            with self.subTest(value=value), self.assertRaises(BinderCoverError):
                parse_spine_width(value)

    def test_interactive_prompt_retries_invalid_input(self):
        answers = iter(("large", "2"))
        messages = []
        width = ask_spine_width(lambda _prompt: next(answers), messages.append)
        self.assertEqual(width, 2.0)
        self.assertEqual(len(messages), 1)

    def test_render_creates_two_letter_pages(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "inserts.pdf"
            render_binder_inserts("Test Binder", 1.5, output)
            reader = PdfReader(str(output))

            text = "\n".join(page.extract_text() for page in reader.pages)
            self.assertIn("PINBALL COMMENTARY", text)
            self.assertIn("A GUIDE TO THE GAMES", text)
            self.assertNotRegex(text, r"\b\d+ GAMES\b")

        self.assertEqual(len(reader.pages), 2)
        for page in reader.pages:
            self.assertAlmostEqual(float(page.mediabox.width), 612)
            self.assertAlmostEqual(float(page.mediabox.height), 792)

    def test_build_uses_saved_title_and_prompts_when_size_is_omitted(self):
        binder = Binder(
            2,
            "test-binder",
            "Test Binder",
            "draft",
            None,
            BinderSource("manual"),
            (BinderEntry("alpha", ("2", "3")),),
        )
        output = Path("/project/output")
        with (
            patch.object(build, "OUTPUT", output),
            patch.object(build, "load_binder", return_value=binder),
            patch.object(build, "ask_spine_width", return_value=1.5) as ask,
            patch.object(build, "render_binder_inserts") as render,
        ):
            result = build.build_binder_cover("test-binder")

        ask.assert_called_once_with()
        self.assertEqual(result, output / "binders/test-binder-inserts-1.5in.pdf")
        render.assert_called_once_with("Test Binder", 1.5, result)

    def test_cli_dispatches_cover_generation(self):
        with patch.object(cli, "build_binder_cover", return_value=Path("cover.pdf")) as cover:
            self.assertEqual(cli.main(["binder", "cover", "test-binder", "--size", "2"]), 0)
        cover.assert_called_once_with("test-binder", "2")


if __name__ == "__main__":
    unittest.main()
