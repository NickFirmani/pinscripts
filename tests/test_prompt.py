import json
import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import main as app
from main import (
    FORMAT_PROMPT_TEMPLATE,
    RESEARCH_PROMPT_TEMPLATE,
    formatting_prompt,
    interactive_research_prompt,
    load_schema,
    read_prompt_input,
    research_prompt,
)


class PromptTests(unittest.TestCase):
    def test_research_prompt_embeds_game_without_schema(self):
        prompt = research_prompt("Jaws (Stern, 2024)")

        self.assertIn("Jaws (Stern, 2024)", prompt)
        self.assertNotIn("{{GAME}}", prompt)
        self.assertNotIn("JSON Schema", prompt)
        self.assertIn("semi-structured research brief", prompt)
        self.assertIn("## Sources", prompt)

    def test_formatting_prompt_embeds_research_and_current_schema(self):
        research = "## Identity and versions\nJaws, Stern, 2024"
        prompt = formatting_prompt(research)

        self.assertIn(research, prompt)
        self.assertNotIn("{{RESEARCH}}", prompt)
        self.assertNotIn("{{SCHEMA}}", prompt)

        embedded_schema = prompt.split("```json\n", 1)[1].split("\n```", 1)[0]
        self.assertEqual(json.loads(embedded_schema), load_schema())

    def test_format_template_does_not_duplicate_schema_constraints(self):
        template = FORMAT_PROMPT_TEMPLATE.read_text(encoding="utf-8")

        self.assertIn("{{SCHEMA}}", template)
        self.assertNotIn("Maximum 5 `rules.bullets`", template)
        self.assertNotIn("risk: Low|Medium", template)

    def test_research_template_has_no_schema_placeholder(self):
        template = RESEARCH_PROMPT_TEMPLATE.read_text(encoding="utf-8")

        self.assertIn("{{GAME}}", template)
        self.assertNotIn("{{SCHEMA}}", template)

    def test_read_prompt_input_reads_a_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "research.md"
            path.write_text("researched facts", encoding="utf-8")

            self.assertEqual(read_prompt_input(str(path)), "researched facts")

    def test_interactive_research_prompt_copies_after_yes(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            research_directory = Path(directory) / "research"
            with (
                patch(
                    "builtins.input",
                    side_effect=[
                        "yes",
                        "",
                        "# Jaws research",
                        "",
                        "Detailed findings.",
                        "::end",
                    ],
                ),
                patch.object(app, "RESEARCH", research_directory),
                patch.object(app, "copy_to_clipboard") as copy,
                redirect_stdout(stdout),
                redirect_stderr(stderr),
            ):
                result = interactive_research_prompt("Jaws Premium 2024")

            saved = research_directory / "jaws-premium-2024.md"
            self.assertEqual(
                saved.read_text(encoding="utf-8"),
                "# Jaws research\n\nDetailed findings.\n",
            )

        self.assertEqual(result, 0)
        prompt = research_prompt("Jaws Premium 2024")
        self.assertIn(prompt, stdout.getvalue())
        copy.assert_called_once_with(prompt)
        self.assertIn("Prompt copied to clipboard", stderr.getvalue())
        self.assertIn("Research response saved", stdout.getvalue())

    def test_interactive_research_prompt_does_not_overwrite_without_confirmation(self):
        with tempfile.TemporaryDirectory() as directory:
            research_directory = Path(directory)
            existing = research_directory / "jaws.md"
            existing.write_text("existing research\n", encoding="utf-8")
            with (
                patch("builtins.input", side_effect=["y", "jaws", "n"]),
                patch.object(app, "RESEARCH", research_directory),
                patch.object(app, "copy_to_clipboard"),
                redirect_stdout(io.StringIO()),
                redirect_stderr(io.StringIO()),
            ):
                result = interactive_research_prompt("Jaws")

            self.assertEqual(existing.read_text(encoding="utf-8"), "existing research\n")

        self.assertEqual(result, 1)

    def test_interactive_research_prompt_does_not_copy_by_default(self):
        with (
            patch("builtins.input", return_value=""),
            patch.object(app, "copy_to_clipboard") as copy,
            redirect_stdout(io.StringIO()),
            redirect_stderr(io.StringIO()),
        ):
            result = interactive_research_prompt("Jaws")

        self.assertEqual(result, 0)
        copy.assert_not_called()

    def test_interactive_research_prompt_treats_eof_as_no(self):
        with (
            patch("builtins.input", side_effect=EOFError),
            patch.object(app, "copy_to_clipboard") as copy,
            redirect_stdout(io.StringIO()),
            redirect_stderr(io.StringIO()),
        ):
            result = interactive_research_prompt("Jaws")

        self.assertEqual(result, 0)
        copy.assert_not_called()

    def test_interactive_research_prompt_asks_for_missing_game(self):
        stdout = io.StringIO()
        with (
            patch("builtins.input", side_effect=["Jaws Premium 2024", "n"]),
            patch.object(app, "copy_to_clipboard") as copy,
            redirect_stdout(stdout),
            redirect_stderr(io.StringIO()),
        ):
            result = interactive_research_prompt("")

        self.assertEqual(result, 0)
        self.assertIn("Jaws Premium 2024", stdout.getvalue())
        copy.assert_not_called()

    def test_interactive_research_prompt_rejects_empty_game(self):
        with (
            patch("builtins.input", return_value=""),
            redirect_stdout(io.StringIO()),
            redirect_stderr(io.StringIO()) as stderr,
        ):
            result = interactive_research_prompt("")

        self.assertEqual(result, 2)
        self.assertIn("game description is required", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
