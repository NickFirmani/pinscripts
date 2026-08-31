import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import benchmarks.format_prompt as harness
from benchmarks.format_prompt import (
    create_run_directory,
    parse_model_output,
    prompt_for_mode,
    response_metrics,
    safe_component,
    schema_errors,
)
from main import load_schema


class FormatHarnessTests(unittest.TestCase):
    def test_structured_prompt_requests_json_and_embeds_research(self):
        prompt = prompt_for_mode("researched facts", "structured-json")

        self.assertIn("Return ONLY a JSON object", prompt)
        self.assertNotIn("Return ONLY YAML", prompt)
        self.assertIn("researched facts", prompt)

    def test_direct_yaml_mode_preserves_production_prompt(self):
        prompt = prompt_for_mode("researched facts", "direct-yaml")

        self.assertIn("Return ONLY YAML", prompt)
        self.assertIn("researched facts", prompt)

    def test_parse_model_output_supports_both_modes(self):
        structured = {"message": {"content": '{"name": "Jaws"}'}}
        direct = {"message": {"content": "name: Jaws\n"}}

        self.assertEqual(
            parse_model_output(structured, "structured-json"),
            {"name": "Jaws"},
        )
        self.assertEqual(
            parse_model_output(direct, "direct-yaml"),
            {"name": "Jaws"},
        )

    def test_empty_content_reports_thinking_length(self):
        payload = {"message": {"content": "", "thinking": "hidden reasoning"}}

        with self.assertRaisesRegex(ValueError, "16 characters"):
            parse_model_output(payload, "structured-json")

    def test_schema_errors_include_paths(self):
        errors = schema_errors({"shots": [{"risk": "Very High"}]}, load_schema())

        self.assertTrue(any("$.shots[0].risk" in error for error in errors), errors)

    def test_response_metrics_converts_ollama_durations(self):
        metrics = response_metrics(
            {
                "eval_count": 20,
                "eval_duration": 2_000_000_000,
                "load_duration": 500_000_000,
            },
            3.0,
        )

        self.assertEqual(metrics["eval_seconds"], 2.0)
        self.assertEqual(metrics["load_seconds"], 0.5)
        self.assertEqual(metrics["output_tokens_per_second"], 10.0)

    def test_run_directory_is_repo_style_and_collision_safe(self):
        when = datetime(2026, 8, 31, 12, 0, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as directory:
            first = create_run_directory(
                Path(directory),
                Path("jaws.md"),
                "qwen3.5:9b",
                "structured-json",
                now=when,
            )
            second = create_run_directory(
                Path(directory),
                Path("jaws.md"),
                "qwen3.5:9b",
                "structured-json",
                now=when,
            )

        self.assertEqual(
            first.name,
            "20260831T120000Z--qwen3.5-9b--structured-json",
        )
        self.assertTrue(second.name.endswith("--2"))

    def test_safe_component_removes_path_syntax(self):
        self.assertEqual(safe_component("registry/model:tag"), "registry-model-tag")

    def test_main_prints_progress_before_and_after_request(self):
        response = {"message": {"content": "{}"}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            research = root / "research.md"
            research.write_text("researched facts", encoding="utf-8")
            stderr = io.StringIO()
            stdout = io.StringIO()
            with (
                patch.object(
                    harness,
                    "ollama_request",
                    return_value=(response, 0.25),
                ),
                patch.object(harness, "schema_errors", return_value=[]),
                redirect_stderr(stderr),
                redirect_stdout(stdout),
            ):
                result = harness.main(
                    [
                        "--model",
                        "test-model",
                        "--research",
                        str(research),
                        "--results-dir",
                        str(root / "results"),
                        "--progress-interval",
                        "0",
                    ]
                )

        self.assertEqual(result, 0)
        self.assertIn("Starting format benchmark", stderr.getvalue())
        self.assertIn("Submitting request to Ollama", stderr.getvalue())
        self.assertIn("Response received after 0.2s", stderr.getvalue())
        self.assertIn("Schema validation passed", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
