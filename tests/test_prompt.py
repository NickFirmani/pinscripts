import json
import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import pinscripts.ai as app
from pinscripts.ai import (
    FORMAT_PROMPT_TEMPLATE,
    RESEARCH_PROMPT_TEMPLATE,
    formatting_prompt,
    interactive_game_format,
    interactive_research_prompt,
    read_prompt_input,
    research_prompt,
    set_terminal_title,
)
from pinscripts.content import load_schema, load_yaml


class PromptTests(unittest.TestCase):
    def test_terminal_title_uses_game_name_on_a_tty(self):
        class TtyBuffer(io.StringIO):
            def isatty(self):
                return True

        stream = TtyBuffer()

        self.assertTrue(set_terminal_title("JAWS (Stern, 2024)", stream))
        self.assertEqual(stream.getvalue(), "\033]0;JAWS (Stern, 2024)\007")

    def test_terminal_title_is_not_written_when_redirected(self):
        stream = io.StringIO()

        self.assertFalse(set_terminal_title("Jaws", stream))
        self.assertEqual(stream.getvalue(), "")

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

    def test_research_template_requires_skill_shot_and_feature_audits(self):
        template = RESEARCH_PROMPT_TEMPLATE.read_text(encoding="utf-8")

        self.assertIn("## Skill shots", template)
        self.assertIn("normal, super, alternate, or secret skill shot", template)
        self.assertIn("## Secondary features", template)
        self.assertIn("ball saves", template)
        self.assertIn("video or display-controlled modes", template)
        self.assertIn("Write `None found`", template)

    def test_format_template_separates_skill_shots_from_features(self):
        template = FORMAT_PROMPT_TEMPLATE.read_text(encoding="utf-8")
        compact = " ".join(template.split())

        self.assertIn("skill shots to `skill_shots`", compact)
        self.assertIn("secondary features to `features`", compact)
        self.assertIn("Never put a skill shot in `features`", template)
        self.assertIn("Always emit both `skill_shots` and `features`", template)

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
                        "none",
                        "::end",
                        "n",
                    ],
                ),
                patch.object(app, "RESEARCH", research_directory),
                patch.object(app, "CONTENT", Path(directory)),
                patch.object(app, "copy_to_clipboard") as copy,
                redirect_stdout(stdout),
                redirect_stderr(stderr),
            ):
                result = interactive_research_prompt("Jaws Premium 2024")

            saved = research_directory / "jaws-premium-2024.md"
            self.assertEqual(
                saved.read_text(encoding="utf-8"),
                "# Jaws research\n\nDetailed findings.\n\n"
                "## Human resolutions\n\nnone\n",
            )

        self.assertEqual(result, 0)
        prompt = research_prompt("Jaws Premium 2024")
        self.assertIn(prompt, stdout.getvalue())
        copy.assert_called_once_with(prompt)
        self.assertIn("Prompt copied to clipboard", stderr.getvalue())
        self.assertIn("Research response saved", stdout.getvalue())

    def test_interactive_research_prompt_formats_json_and_writes_yaml(self):
        formatted = load_yaml(app.CONTENT / "playboy-bally-1978.yaml")
        formatted.update(
            {
                "id": "jaws-2024",
                "name": "JAWS",
                "manufacturer": "Stern",
                "year": 2024,
                "image": "images/jaws-2024.webp",
            }
        )
        with tempfile.TemporaryDirectory() as directory:
            content = Path(directory) / "content"
            research_directory = content / "research"
            with (
                patch(
                    "builtins.input",
                    side_effect=[
                        "y",
                        "jaws-2024",
                        "# Researched JAWS facts",
                        "::end",
                        "The tournament is using the Premium model.",
                        "::end",
                        "y",
                        "```json",
                        json.dumps(formatted),
                        "```",
                        "::end",
                    ],
                ),
                patch.object(app, "CONTENT", content),
                patch.object(app, "RESEARCH", research_directory),
                patch.object(app, "copy_to_clipboard") as copy,
                redirect_stdout(io.StringIO()) as stdout,
                redirect_stderr(io.StringIO()),
            ):
                result = interactive_research_prompt("JAWS (Stern, 2024)")

            output = content / "jaws-2024.yaml"
            self.assertEqual(load_yaml(output), formatted)

        self.assertEqual(result, 0)
        self.assertEqual(copy.call_count, 2)
        formatting_copy = copy.call_args_list[1].args[0]
        self.assertIn("Return ONLY a JSON object", formatting_copy)
        self.assertIn("Set `id` exactly to `jaws-2024`", formatting_copy)
        self.assertIn("## Human resolutions", formatting_copy)
        self.assertIn("Premium model", formatting_copy)
        self.assertIn("Formatted YAML saved", stdout.getvalue())

    def test_human_questions_are_extracted_and_resolutions_precede_sources(self):
        research = (
            "## Identity and versions\nFacts\n\n"
            "## Questions for the humans\n\n"
            "### Tournament and venue checks\n\nWhich model is present?\n\n"
            "## Sources\n\nS1: source"
        )

        self.assertIn("Which model is present?", app.human_questions(research))
        resolved = app.add_human_resolutions(research, "Premium model.")
        self.assertLess(
            resolved.index("## Human resolutions"),
            resolved.index("## Sources"),
        )
        self.assertIn("Premium model.", resolved)
        self.assertEqual(app.human_resolutions(resolved), "Premium model.")

    def test_numbered_human_questions_include_their_choices(self):
        research = (
            "## Questions for the humans\n\n"
            "### Tournament and venue checks\n\n"
            "1. **Installed code?**\n"
            "   A. v1.02.0\n"
            "   B. Unknown\n\n"
            "2. **Extra balls?**\n"
            "   A. Disabled\n"
            "   B. Enabled\n\n"
            "### Uncertainties and conflicts\n\n"
            "* This should not become part of question two.\n\n"
            "## Sources\nS1\n"
        )

        questions = app.numbered_human_questions(research)

        self.assertEqual(len(questions), 2)
        self.assertIn("A. v1.02.0", questions[0])
        self.assertIn("B. Enabled", questions[1])
        self.assertNotIn("Uncertainties", questions[1])

    def test_human_resolutions_prompt_for_each_numbered_question(self):
        research = (
            "## Questions for the humans\n\n"
            "1. **Installed code?**\n"
            "   A. v1.02.0\n"
            "   B. Unknown\n\n"
            "2. **Extra balls?**\n"
            "   A. Disabled\n"
            "   B. Enabled\n\n"
            "## Sources\nS1\n"
        )
        with (
            patch("builtins.input", side_effect=["a", "Enabled at venue"]),
            redirect_stdout(io.StringIO()) as stdout,
        ):
            resolutions = app.request_human_resolutions(research)

        self.assertIn("Question 1 of 2", stdout.getvalue())
        self.assertIn("Question 2 of 2", stdout.getvalue())
        self.assertIn("**Human answer:** A. v1.02.0", resolutions)
        self.assertIn("**Human answer:** Enabled at venue", resolutions)

    def test_game_format_uses_existing_research_and_human_resolutions(self):
        formatted = load_yaml(app.CONTENT / "playboy-bally-1978.yaml")
        formatted.update(
            {
                "id": "jaws-2024",
                "name": "JAWS",
                "manufacturer": "Stern",
                "year": 2024,
                "image": "images/jaws-2024.webp",
            }
        )
        research = (
            "## Identity and versions\nFacts\n\n"
            "## Human resolutions\n\nPremium model.\n\n"
            "## Sources\nSources\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            content = Path(directory) / "content"
            research_directory = content / "research"
            research_directory.mkdir(parents=True)
            research_path = research_directory / "jaws-2024.md"
            research_path.write_text(research, encoding="utf-8")
            with (
                patch(
                    "builtins.input",
                    side_effect=["y", json.dumps(formatted), "::end"],
                ),
                patch.object(app, "CONTENT", content),
                patch.object(app, "RESEARCH", research_directory),
                patch.object(app, "copy_to_clipboard") as copy,
                redirect_stdout(io.StringIO()) as stdout,
                redirect_stderr(io.StringIO()),
            ):
                result = interactive_game_format("jaws-2024")

            self.assertEqual(load_yaml(content / "jaws-2024.yaml"), formatted)
            self.assertEqual(research_path.read_text(encoding="utf-8"), research)

        self.assertEqual(result, 0)
        copy.assert_called_once()
        self.assertIn("Using the human resolutions already saved", stdout.getvalue())

    def test_game_format_collects_missing_human_resolutions(self):
        with tempfile.TemporaryDirectory() as directory:
            content = Path(directory) / "content"
            research_directory = content / "research"
            research_directory.mkdir(parents=True)
            research_path = research_directory / "jaws-2024.md"
            research_path.write_text(
                "## Questions for the humans\n\nWhich trim?\n\n## Sources\nS1\n",
                encoding="utf-8",
            )
            with (
                patch(
                    "builtins.input",
                    side_effect=["Premium", "::end", "n"],
                ),
                patch.object(app, "CONTENT", content),
                patch.object(app, "RESEARCH", research_directory),
                redirect_stdout(io.StringIO()),
                redirect_stderr(io.StringIO()),
            ):
                result = interactive_game_format("jaws-2024")

            saved = research_path.read_text(encoding="utf-8")

        self.assertEqual(result, 0)
        self.assertIn("## Human resolutions\n\nPremium", saved)
        self.assertLess(saved.index("## Human resolutions"), saved.index("## Sources"))

    def test_game_format_rejects_missing_research_file(self):
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(app, "RESEARCH", Path(directory)),
                redirect_stderr(io.StringIO()) as stderr,
            ):
                result = interactive_game_format("missing-game")

        self.assertEqual(result, 1)
        self.assertIn("could not read research brief", stderr.getvalue())

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

    def test_interactive_research_prompt_copies_by_default(self):
        with (
            patch("builtins.input", return_value=""),
            patch.object(app, "copy_to_clipboard") as copy,
            patch.object(app, "request_research_path", return_value=None),
            patch.object(app, "set_terminal_title") as set_title,
            redirect_stdout(io.StringIO()),
            redirect_stderr(io.StringIO()),
        ):
            result = interactive_research_prompt("Jaws")

        self.assertEqual(result, 1)
        copy.assert_called_once_with(research_prompt("Jaws"))
        set_title.assert_called_once_with("Jaws")

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
            patch.object(app, "set_terminal_title") as set_title,
            redirect_stdout(stdout),
            redirect_stderr(io.StringIO()),
        ):
            result = interactive_research_prompt("")

        self.assertEqual(result, 0)
        self.assertIn("Jaws Premium 2024", stdout.getvalue())
        copy.assert_not_called()
        set_title.assert_called_once_with("Jaws Premium 2024")

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
