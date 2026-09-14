import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pinscripts.binder_workflows as app
from pinscripts.binder import Binder, BinderSource, PendingGame, SourceOverride
from pinscripts.catalog import CatalogGame, match_imported_game
from pinscripts.pinball_map import ImportedGame, ImportedLocation


class BinderWorkflowTests(unittest.TestCase):
    def test_matching_normalizes_manufacturer_legal_names(self):
        catalog = {
            "addams-family-bally-1992": CatalogGame(
                "addams-family-bally-1992",
                "The Addams Family",
                "Bally/Midway",
                1992,
                Path("content/addams-family-bally-1992.yaml"),
            )
        }
        imported = ImportedGame("The Addams Family", "Bally", 1992)

        self.assertEqual(
            match_imported_game(imported, catalog).game_id,
            "addams-family-bally-1992",
        )

    def test_matching_keeps_stern_pro_separate_from_premium_le(self):
        catalog = {
            "jaws-pro-stern-2024": CatalogGame(
                "jaws-pro-stern-2024",
                "JAWS (Pro)",
                "Stern Pinball",
                2024,
                Path("content/jaws-pro-stern-2024.yaml"),
            )
        }

        self.assertIsNone(
            match_imported_game(ImportedGame("JAWS (LE)", "Stern", 2024), catalog)
        )

    def test_matching_deduplicates_stern_premium_and_le(self):
        catalog = {
            "jaws-prem-le-stern-2024": CatalogGame(
                "jaws-prem-le-stern-2024",
                "JAWS (Prem/LE)",
                "Stern Pinball",
                2024,
                Path("content/jaws-prem-le-stern-2024.yaml"),
            )
        }

        for imported_name in ("JAWS (Premium)", "JAWS (LE)"):
            with self.subTest(imported_name=imported_name):
                self.assertEqual(
                    match_imported_game(
                        ImportedGame(imported_name, "Stern", 2024),
                        catalog,
                    ).game_id,
                    "jaws-prem-le-stern-2024",
                )

    def test_matching_deduplicates_batman_catwoman_signature_edition(self):
        catalog = {
            "batman-66-prem-le-stern-2016": CatalogGame(
                "batman-66-prem-le-stern-2016",
                "Batman ’66 (Prem/LE)",
                "Stern Pinball",
                2016,
                Path("content/batman-66-prem-le-stern-2016.yaml"),
            )
        }

        match = match_imported_game(
            ImportedGame(
                "Batman 66 (Catwoman Signature Edition)",
                "Stern",
                2019,
            ),
            catalog,
        )

        self.assertEqual(match.game_id, "batman-66-prem-le-stern-2016")

    def test_matching_deduplicates_jersey_jack_le_and_ce_but_not_se(self):
        catalog = {
            "avatar-le-ce-jersey-jack-2024": CatalogGame(
                "avatar-le-ce-jersey-jack-2024",
                "Avatar: The Battle for Pandora (LE/CE)",
                "Jersey Jack Pinball",
                2024,
                Path("content/avatar-le-ce-jersey-jack-2024.yaml"),
            )
        }

        self.assertIsNotNone(
            match_imported_game(
                ImportedGame("Avatar: The Battle for Pandora (CE)", "Jersey Jack", 2024),
                catalog,
            )
        )
        self.assertIsNone(
            match_imported_game(
                ImportedGame("Avatar: The Battle for Pandora (SE)", "Jersey Jack", 2024),
                catalog,
            )
        )

    def test_classification_honors_replace_and_ignore_overrides(self):
        wrong = PendingGame("Wrong Game", "Bally", 1980)
        renamed = PendingGame("Venue Name", "Bally", 1981)
        binder = Binder(
            2,
            "test-binder",
            "Test Binder",
            "draft",
            None,
            BinderSource("manual", "123"),
            (),
            (),
            (
                SourceOverride(wrong, "ignore", reason="Not present."),
                SourceOverride(renamed, "replace", "alpha", "Corrected name."),
            ),
        )
        imported = ImportedLocation(
            "123",
            "Test Binder",
            "https://pinballmap.com/map/?by_location_id=123",
            "2026-09-13",
            (
                ImportedGame(wrong.name, wrong.manufacturer, wrong.year),
                ImportedGame(renamed.name, renamed.manufacturer, renamed.year),
                ImportedGame("Unknown", "Bally", 1982),
            ),
        )
        catalog = {
            "alpha": CatalogGame("alpha", "Alpha", "Bally", 1981, Path("alpha.yaml"))
        }

        with patch.object(app, "catalog_by_id", return_value=catalog):
            resolved, pending, ignored = app.classify_imported(imported, binder)

        self.assertEqual([(item.key, game_id, overridden) for item, game_id, overridden in resolved], [(renamed.key, "alpha", True)])
        self.assertEqual([item.name for item in pending], ["Unknown"])
        self.assertEqual(ignored, [wrong])

    def test_create_queues_unmatched_imports_without_inline_research(self):
        imported = ImportedLocation(
            "123",
            "Test Venue",
            "https://pinballmap.com/map/?by_location_id=123",
            "2026-09-13",
            (
                ImportedGame("Alpha", "Bally", 1980),
                ImportedGame("Unknown", "Bally", 1981),
            ),
        )
        catalog = {
            "alpha": CatalogGame("alpha", "Alpha", "Bally", 1980, Path("alpha.yaml"))
        }
        with TemporaryDirectory() as directory:
            destination = Path(directory) / "test-venue.yaml"
            with (
                patch.object(app, "binder_path", return_value=destination),
                patch.object(app, "_load_import", return_value=imported),
                patch.object(app, "catalog_by_id", return_value=catalog),
                patch.object(app, "write_binder", return_value=destination) as write,
            ):
                result = app.create_binder_interactive(
                    "test-venue",
                    pinball_map="123",
                )

        binder = write.call_args.args[0]
        self.assertEqual(result, 0)
        self.assertEqual([entry.game_id for entry in binder.games], ["alpha"])
        self.assertEqual([item.name for item in binder.pending_games], ["Unknown"])


if __name__ == "__main__":
    unittest.main()
