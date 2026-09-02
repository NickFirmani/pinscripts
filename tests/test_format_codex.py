import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from benchmarks.format_codex import (
    contains_rate_limit,
    create_run_directory,
    parse_event_usage,
    promotion_ready_research,
)


class CodexFormatHarnessTests(unittest.TestCase):
    def test_promotion_ready_research_skips_existing_and_unresolved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            research = root / "research"
            content = root / "content"
            research.mkdir()
            content.mkdir()
            (research / "ready.md").write_text(
                "## Human resolutions\n\nConfirmed venue setup.\n",
                encoding="utf-8",
            )
            (research / "existing.md").write_text(
                "## Human resolutions\n\nConfirmed.\n",
                encoding="utf-8",
            )
            (research / "unresolved.md").write_text(
                "## Identity and versions\n\nFacts.\n",
                encoding="utf-8",
            )
            (content / "existing.yaml").touch()

            ready, skipped = promotion_ready_research(research, content)

        self.assertEqual([path.stem for path in ready], ["ready"])
        self.assertEqual(
            {(entry["id"], entry["reason"]) for entry in skipped},
            {
                ("existing", "content exists"),
                ("unresolved", "no human resolutions"),
            },
        )

    def test_create_run_directory_is_collision_safe(self):
        when = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as directory:
            first = create_run_directory(
                directory, "game-id", "gpt-5.6-terra", "medium", now=when
            )
            second = create_run_directory(
                directory, "game-id", "gpt-5.6-terra", "medium", now=when
            )

        self.assertEqual(
            first.name,
            "20260901T120000Z--gpt-5.6-terra-medium--structured-json",
        )
        self.assertTrue(second.name.endswith("--2"))

    def test_parse_event_usage_reads_completed_turn(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            path.write_text(
                json.dumps({"type": "turn.started"})
                + "\n"
                + json.dumps(
                    {
                        "type": "turn.completed",
                        "usage": {"input_tokens": 10, "output_tokens": 2},
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            usage = parse_event_usage(path)

        self.assertEqual(usage, {"input_tokens": 10, "output_tokens": 2})

    def test_rate_limit_detection_accepts_cli_error_shapes(self):
        self.assertTrue(contains_rate_limit('{"code":"rate_limit_exceeded"}'))
        self.assertTrue(contains_rate_limit("Usage limit reached"))
        self.assertFalse(contains_rate_limit("temporary server error"))


if __name__ == "__main__":
    unittest.main()
