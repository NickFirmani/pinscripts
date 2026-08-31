import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

import main as app
from main import CONTENT, schema_validator, validate_content


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
                patch.object(app, "CONTENT", content),
                patch.object(app, "render") as render,
                patch.object(sys, "argv", ["main.py", "broken"]),
                redirect_stderr(io.StringIO()),
            ):
                result = app.main()

        self.assertEqual(result, 1)
        render.assert_not_called()

    def validate_text(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "game.yaml"
            path.write_text(text, encoding="utf-8")
            return validate_content(path, self.validator)


if __name__ == "__main__":
    unittest.main()
