import tempfile
import unittest
from pathlib import Path

from pinscripts.catalog import (
    CatalogError,
    CatalogGame,
    load_catalog,
    similar_catalog_games,
)


class CatalogTests(unittest.TestCase):
    def test_similarity_finds_other_editions_of_a_close_name(self):
        catalog = {
            "jaws-pro-stern-2024": CatalogGame(
                "jaws-pro-stern-2024",
                "JAWS (Pro)",
                "Stern Pinball",
                2024,
                Path("jaws-pro-stern-2024.yaml"),
            ),
            "jaws-prem-le-stern-2024": CatalogGame(
                "jaws-prem-le-stern-2024",
                "JAWS (Prem/LE)",
                "Stern Pinball",
                2024,
                Path("jaws-prem-le-stern-2024.yaml"),
            ),
            "james-bond-pro-stern-2022": CatalogGame(
                "james-bond-pro-stern-2022",
                "James Bond 007 (Pro)",
                "Stern Pinball",
                2022,
                Path("james-bond-pro-stern-2022.yaml"),
            ),
        }

        suggestions = similar_catalog_games(
            "JAWS (LE)",
            catalog,
            manufacturer="Stern",
            year=2024,
        )

        self.assertEqual(
            [game.game_id for game in suggestions],
            ["jaws-prem-le-stern-2024", "jaws-pro-stern-2024"],
        )

    def test_catalog_rejects_equivalent_trim_duplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            content = Path(directory)
            (content / "jaws-premium.yaml").write_text(
                "id: jaws-premium\n"
                "name: JAWS (Premium)\n"
                "metadata:\n"
                "  manufacturer: Stern Pinball\n"
                "  year: 2024\n",
                encoding="utf-8",
            )
            (content / "jaws-le.yaml").write_text(
                "id: jaws-le\n"
                "name: JAWS (LE)\n"
                "metadata:\n"
                "  manufacturer: Stern Pinball\n"
                "  year: 2024\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(CatalogError, "must be deduplicated"):
                load_catalog(content)

    def test_catalog_rejects_batman_catwoman_signature_duplicate(self):
        with tempfile.TemporaryDirectory() as directory:
            content = Path(directory)
            (content / "batman-prem-le.yaml").write_text(
                "id: batman-prem-le\n"
                "name: Batman 66 (Prem/LE)\n"
                "metadata:\n"
                "  manufacturer: Stern Pinball\n"
                "  year: 2016\n",
                encoding="utf-8",
            )
            (content / "batman-catwoman.yaml").write_text(
                "id: batman-catwoman\n"
                "name: Batman 66 (Catwoman Signature Edition)\n"
                "metadata:\n"
                "  manufacturer: Stern\n"
                "  year: 2019\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(CatalogError, "must be deduplicated"):
                load_catalog(content)


if __name__ == "__main__":
    unittest.main()
