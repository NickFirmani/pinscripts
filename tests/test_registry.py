import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pinscripts.content as app


class RegistryTests(unittest.TestCase):
    def test_empty_enabled_selects_all_content_except_disabled(self):
        with self.registry(
            "enabled: []\ndisabled:\n  - beta\n",
            ["zeta", "beta", "alpha"],
        ):
            paths = app.content_for_selected_pins()

        self.assertEqual([path.stem for path in paths], ["alpha", "zeta"])

    def test_nonempty_enabled_is_an_ordered_allowlist(self):
        with self.registry(
            "enabled:\n  - zeta\n  - alpha\ndisabled: []\n",
            ["alpha", "beta", "zeta"],
        ):
            paths = app.content_for_selected_pins()

        self.assertEqual([path.stem for path in paths], ["zeta", "alpha"])

    def test_explicitly_enabled_pin_requires_content(self):
        with self.registry(
            "enabled:\n  - missing-game\ndisabled: []\n",
            [],
        ):
            with self.assertRaisesRegex(
                app.PinRegistryError,
                "missing-game",
            ):
                app.content_for_selected_pins()

    def test_disabled_pin_does_not_require_content(self):
        with self.registry(
            "enabled: []\ndisabled:\n  - future-game\n",
            [],
        ):
            self.assertEqual(app.content_for_selected_pins(), [])

    def test_pin_cannot_be_enabled_and_disabled(self):
        with self.registry(
            "enabled:\n  - same-game\ndisabled:\n  - same-game\n",
            ["same-game"],
        ):
            with self.assertRaisesRegex(app.PinRegistryError, "both enabled"):
                app.content_for_selected_pins()

    def test_duplicate_and_invalid_ids_are_rejected(self):
        cases = [
            (
                "enabled:\n  - same-game\n  - same-game\ndisabled: []\n",
                "duplicate",
            ),
            (
                "enabled: []\ndisabled:\n  - Not Valid\n",
                "invalid pin IDs",
            ),
        ]

        for registry, message in cases:
            with self.subTest(message=message):
                with self.registry(registry, []):
                    with self.assertRaisesRegex(app.PinRegistryError, message):
                        app.content_for_selected_pins()

    def test_registry_requires_exact_top_level_keys(self):
        cases = [
            ("enabled: []\n", "missing keys: disabled"),
            (
                "enabled: []\ndisabled: []\npins: []\n",
                "unknown keys: pins",
            ),
        ]

        for registry, message in cases:
            with self.subTest(message=message):
                with self.registry(registry, []):
                    with self.assertRaisesRegex(app.PinRegistryError, message):
                        app.content_for_selected_pins()

    def registry(self, registry, content_ids):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        manifest = root / "pins.yaml"
        content = root / "content"
        content.mkdir()
        manifest.write_text(registry, encoding="utf-8")

        for pin_id in content_ids:
            (content / f"{pin_id}.yaml").touch()

        manifest_patch = patch.object(app, "MANIFEST", manifest)
        content_patch = patch.object(app, "CONTENT", content)

        class RegistryContext:
            def __enter__(self):
                temporary.__enter__()
                manifest_patch.start()
                content_patch.start()

            def __exit__(self, *args):
                content_patch.stop()
                manifest_patch.stop()
                temporary.__exit__(*args)

        return RegistryContext()


if __name__ == "__main__":
    unittest.main()
