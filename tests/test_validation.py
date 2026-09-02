import io
import sys
import tempfile
import unittest
from copy import deepcopy
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

import main as cli
import pinscripts.build as builder
import pinscripts.content as app
from pinscripts.content import load_schema, schema_validator, validate_content
from pinscripts.paths import CONTENT


class ValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = schema_validator()

    def test_existing_content_is_valid(self):
        errors = validate_content(
            CONTENT / "playboy-bally-1978.yaml",
            self.validator,
        )

        self.assertEqual(errors, [])

    def test_schema_is_openai_structured_outputs_compatible(self):
        forbidden_keywords = {
            "allOf",
            "not",
            "dependentRequired",
            "dependentSchemas",
            "if",
            "then",
            "else",
        }

        def check_schema(node, path="$"):
            if isinstance(node, dict):
                forbidden = forbidden_keywords.intersection(node)
                self.assertEqual(
                    forbidden,
                    set(),
                    f"{path} uses unsupported keywords: {sorted(forbidden)}",
                )

                if node.get("type") == "object":
                    properties = set(node.get("properties", {}))
                    required = set(node.get("required", []))
                    self.assertEqual(
                        required,
                        properties,
                        f"{path} must require every declared property",
                    )
                    self.assertIs(
                        node.get("additionalProperties"),
                        False,
                        f"{path} must set additionalProperties to false",
                    )

                for key, value in node.items():
                    check_schema(value, f"{path}.{key}")
            elif isinstance(node, list):
                for index, value in enumerate(node):
                    check_schema(value, f"{path}[{index}]")

        check_schema(load_schema())

    def test_game_without_skill_shots_uses_explicit_empty_array(self):
        data = app.load_yaml(CONTENT / "playboy-bally-1978.yaml")

        self.assertEqual(data["skill_shots"], [])
        self.assertEqual(app.validation_errors(data, self.validator), [])

    def test_skill_shots_and_secondary_features_are_valid(self):
        data = deepcopy(app.load_yaml(CONTENT / "playboy-bally-1978.yaml"))
        data["skill_shots"] = [
            {
                "name": "Super Skill Shot",
                "how": "Hold the left flipper and plunge the flashing lane.",
                "value": "Awards immediate progression and a scoring boost.",
            }
        ]
        data["features"] = [
            {
                "type": "ball-save",
                "name": "Life Ring",
                "text": "Press the action button to rescue a qualified outlane drain.",
            },
            {
                "type": "video-mode",
                "name": "Video Mode",
                "text": "Use the flipper buttons to complete the display objective.",
            },
        ]

        self.assertEqual(app.validation_errors(data, self.validator), [])

    def test_skill_shots_and_features_are_required(self):
        data = deepcopy(app.load_yaml(CONTENT / "playboy-bally-1978.yaml"))
        del data["skill_shots"]
        del data["features"]

        errors = app.validation_errors(data, self.validator)

        self.assertTrue(any("'skill_shots' is a required property" in e for e in errors))
        self.assertTrue(any("'features' is a required property" in e for e in errors))

    def test_skill_shot_cannot_be_encoded_as_a_secondary_feature(self):
        data = deepcopy(app.load_yaml(CONTENT / "playboy-bally-1978.yaml"))
        data["features"] = [
            {
                "type": "skill-shot",
                "name": "Skill Shot",
                "text": "This belongs in the first-class skill_shots field.",
            }
        ]

        errors = app.validation_errors(data, self.validator)

        self.assertTrue(any("$.features[0].type" in error for error in errors), errors)

    def test_schema_errors_include_field_path(self):
        errors = self.validate_text(
            """
id: invalid-id
shots:
  - risk: Very High
"""
        )

        self.assertTrue(
            any("$.shots[0].risk" in error for error in errors),
            errors,
        )

    def test_invalid_yaml_is_reported(self):
        errors = self.validate_text("shots: [\n")

        self.assertEqual(len(errors), 1)
        self.assertTrue(errors[0].startswith("invalid YAML:"), errors)

    def test_render_does_not_run_after_validation_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            content = Path(directory)
            (content / "broken.yaml").write_text(
                "name: Incomplete\n",
                encoding="utf-8",
            )

            with (
                patch.object(builder, "CONTENT", content),
                patch.object(builder, "render") as render,
                patch.object(sys, "argv", ["main.py", "broken"]),
                redirect_stderr(io.StringIO()),
            ):
                result = cli.main()

        self.assertEqual(result, 1)
        render.assert_not_called()

    def validate_text(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "game.yaml"
            path.write_text(text, encoding="utf-8")
            return validate_content(path, self.validator)


if __name__ == "__main__":
    unittest.main()
