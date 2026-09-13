import unittest
from pathlib import Path

from pinscripts.binder_workflows import match_imported_game
from pinscripts.catalog import CatalogGame
from pinscripts.pinball_map import ImportedGame


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

    def test_matching_never_conflates_editions(self):
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


if __name__ == "__main__":
    unittest.main()
