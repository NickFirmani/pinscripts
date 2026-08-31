import json
import unittest

from main import PROMPT_TEMPLATE, generation_prompt, load_schema


class PromptTests(unittest.TestCase):
    def test_generation_prompt_embeds_game_and_current_schema(self):
        prompt = generation_prompt("Jaws (Stern, 2024)")

        self.assertIn("Jaws (Stern, 2024)", prompt)
        self.assertNotIn("{{GAME}}", prompt)
        self.assertNotIn("{{SCHEMA}}", prompt)

        embedded_schema = prompt.split("```json\n", 1)[1].split("\n```", 1)[0]
        self.assertEqual(json.loads(embedded_schema), load_schema())

    def test_template_does_not_duplicate_schema_constraints(self):
        template = PROMPT_TEMPLATE.read_text(encoding="utf-8")

        self.assertIn("{{SCHEMA}}", template)
        self.assertNotIn("Maximum 5 `rules.bullets`", template)
        self.assertNotIn("risk: Low|Medium", template)


if __name__ == "__main__":
    unittest.main()
