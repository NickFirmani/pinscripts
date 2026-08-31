import json
import tempfile
import unittest
from pathlib import Path

from main import (
    FORMAT_PROMPT_TEMPLATE,
    PROMPT_TEMPLATE,
    RESEARCH_PROMPT_TEMPLATE,
    formatting_prompt,
    generation_prompt,
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

    def test_original_prompt_api_is_a_research_prompt_alias(self):
        self.assertEqual(PROMPT_TEMPLATE, RESEARCH_PROMPT_TEMPLATE)
        self.assertEqual(generation_prompt("Jaws"), research_prompt("Jaws"))

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


if __name__ == "__main__":
    unittest.main()
