import tempfile
import unittest
from pathlib import Path

from pinscripts.binder import (
    Binder,
    BinderEntry,
    BinderError,
    BinderSource,
    PendingGame,
    SourceOverride,
    add_game,
    allocate_page_labels,
    binder_data,
    binder_from_data,
    create_binder,
    load_binder,
    mark_printed,
    remove_game,
    write_binder,
)
from pinscripts.catalog import CatalogGame


class BinderTests(unittest.TestCase):
    def setUp(self):
        self.catalog = {
            "alpha": CatalogGame("alpha", "Alpha", "Bally", 1980, Path("alpha.yaml")),
            "bravo": CatalogGame("bravo", "Bravo", "Bally", 1981, Path("bravo.yaml")),
            "charlie": CatalogGame("charlie", "Charlie", "Bally", 1982, Path("charlie.yaml")),
        }

    def test_draft_binder_uses_clean_integer_pages(self):
        binder = create_binder("test-binder", "Test Binder", ["bravo", "alpha"])
        binder = add_game(binder, "charlie", self.catalog)

        self.assertEqual([entry.game_id for entry in binder.games], ["alpha", "bravo", "charlie"])
        self.assertEqual([entry.pages for entry in binder.games], [("2", "3"), ("4", "5"), ("6", "7")])

    def test_printed_binder_add_preserves_old_pages(self):
        binder = mark_printed(create_binder("test-binder", "Test Binder", ["alpha", "charlie"]), "2026-09-13")
        updated = add_game(binder, "bravo", self.catalog)

        self.assertEqual(updated.entry("alpha").pages, ("2", "3"))
        self.assertEqual(updated.entry("bravo").pages, ("3.1", "3.2"))
        self.assertEqual(updated.entry("charlie").pages, ("4", "5"))

    def test_printed_removal_retains_a_page_tombstone(self):
        binder = mark_printed(create_binder("test-binder", "Test Binder", ["alpha", "bravo"]), "2026-09-13")
        updated = remove_game(binder, "alpha", self.catalog)

        self.assertFalse(updated.entry("alpha").present)
        self.assertEqual(updated.entry("alpha").pages, ("2", "3"))
        self.assertEqual([entry.game_id for entry in updated.active_games], ["bravo"])

    def test_source_supports_manual_curation_with_an_advisory_url(self):
        data = {
            "version": 2,
            "id": "test-binder",
            "title": "Test Binder",
            "status": "printed",
            "printed_at": None,
            "source": {
                "kind": "manual",
                "location_id": "25303",
                "url": "https://pinballmap.com/map/?by_location_id=25303",
                "retrieved_at": "2026-09-13",
                "notes": "Manually corrected after checking the venue.",
            },
            "pending_games": [],
            "source_overrides": [],
            "games": [],
        }

        binder = binder_from_data(data, require_content=False)
        self.assertEqual(binder.source.kind, "manual")
        self.assertEqual(binder.source.location_id, "25303")

    def test_write_and_load_round_trip(self):
        binder = Binder(
            2,
            "test-binder",
            "Test Binder",
            "printed",
            None,
            BinderSource("manual"),
            (BinderEntry("alpha", ("2", "3"), True, ("Local note.",)),),
            (PendingGame("Bravo", "Bally", 1981),),
            (
                SourceOverride(
                    PendingGame("Charlie LE", "Bally", 1982),
                    "replace",
                    "charlie",
                    "Venue has the standard edition.",
                ),
            ),
        )
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            content = directory / "content"
            content.mkdir()
            (content / "alpha.yaml").touch()
            (content / "charlie.yaml").touch()
            path = directory / "test-binder.yaml"
            write_binder(binder, path=path)
            loaded = load_binder(path, content_directory=content)

        self.assertEqual(loaded, binder)

    def test_pending_imports_prevent_marking_a_binder_printed(self):
        binder = create_binder(
            "test-binder",
            "Test Binder",
            ["alpha"],
            pending_games=(PendingGame("Bravo", "Bally", 1981),),
        )

        with self.assertRaisesRegex(BinderError, "1 pending game"):
            mark_printed(binder)

    def test_pending_game_and_override_cannot_share_an_import_identity(self):
        pending = PendingGame("Bravo", "Bally", 1981)
        binder = create_binder(
            "test-binder",
            "Test Binder",
            [],
            pending_games=(pending,),
            source_overrides=(SourceOverride(pending, "ignore"),),
        )

        with self.assertRaisesRegex(BinderError, "both pending and overridden"):
            binder_from_data(binder_data(binder), require_content=False)

    def test_page_allocator_supports_repeated_insertions(self):
        self.assertEqual(allocate_page_labels("3", "4"), ("3.1", "3.2"))
        self.assertEqual(allocate_page_labels("3", "3.1"), ("3.01", "3.02"))


if __name__ == "__main__":
    unittest.main()
