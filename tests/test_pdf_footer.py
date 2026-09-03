import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from pypdf import PdfReader, PdfWriter

from pinscripts.pdf import (
    FOOTER_Y,
    INNER_MARGIN,
    OUTER_MARGIN,
    PAGE_W,
    _draw_spread_chrome,
    git_updated_at,
    merge_pdfs,
    rules_footer_text,
)


class PdfFooterTests(unittest.TestCase):
    def test_merged_binder_starts_with_an_unnumbered_title_page(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            game_pdf = directory / "game.pdf"
            output_pdf = directory / "binder.pdf"
            writer = PdfWriter()
            writer.add_blank_page(width=PAGE_W, height=792)
            with game_pdf.open("wb") as stream:
                writer.write(stream)

            merge_pdfs([game_pdf], output_pdf)

            reader = PdfReader(output_pdf)
            self.assertEqual(len(reader.pages), 2)
            self.assertIn(
                "Pinball Commentary Quick Reference",
                reader.pages[0].extract_text(),
            )
            self.assertNotIn("PAGE", reader.pages[0].extract_text())

    def test_code_footer_identifies_both_leaves_and_numbers_binder_pages(self):
        canvas = MagicMock()
        rules_basis = {
            "kind": "code",
            "version": "1.17.0",
            "release_date": "2026-08-14",
        }

        _draw_spread_chrome(
            canvas,
            "Example Game",
            "2026-09-03",
            7,
            rules_basis,
        )

        footer = (
            "EXAMPLE GAME • CODE 1.17.0 • RELEASED 2026-08-14 • "
            "UPDATED AT 2026-09-03"
        )
        canvas.drawString.assert_any_call(
            OUTER_MARGIN,
            FOOTER_Y - 8,
            footer,
        )
        canvas.drawString.assert_any_call(
            PAGE_W + INNER_MARGIN,
            FOOTER_Y - 8,
            footer,
        )
        canvas.drawRightString.assert_any_call(
            PAGE_W - INNER_MARGIN,
            FOOTER_Y - 8,
            "PAGE 7",
        )
        canvas.drawRightString.assert_any_call(
            (2 * PAGE_W) - OUTER_MARGIN,
            FOOTER_Y - 8,
            "PAGE 8",
        )

    def test_rom_footer_uses_git_date_without_release_date(self):
        text = rules_footer_text(
            {"kind": "rom", "version": "L-7", "release_date": None},
            "2026-09-03",
        )

        self.assertEqual(text, "ROM L-7 • UPDATED AT 2026-09-03")

    def test_fixed_rules_have_no_footer_copy_or_separator(self):
        canvas = MagicMock()

        _draw_spread_chrome(
            canvas,
            "Fixed Game",
            None,
            7,
            {"kind": "fixed", "version": None, "release_date": None},
        )

        canvas.line.assert_not_called()
        canvas.drawString.assert_not_called()
        canvas.drawRightString.assert_any_call(
            PAGE_W - INNER_MARGIN,
            FOOTER_Y - 17,
            "PAGE 7",
        )
        canvas.drawRightString.assert_any_call(
            (2 * PAGE_W) - OUTER_MARGIN,
            FOOTER_Y - 17,
            "PAGE 8",
        )

    @patch("pinscripts.pdf.subprocess.run")
    def test_updated_at_comes_from_content_file_git_history(self, run):
        run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="2026-08-31\n",
            stderr="",
        )
        content_path = Path(__file__).parents[1] / "content" / "example.yaml"

        updated_at = git_updated_at(content_path)

        self.assertEqual(updated_at, "2026-08-31")
        command = run.call_args.args[0]
        self.assertEqual(command[-2:], ["--", "content/example.yaml"])


if __name__ == "__main__":
    unittest.main()
