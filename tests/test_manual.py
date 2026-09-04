import tempfile
import unittest
from pathlib import Path

from pinscripts.manual import (
    Manual,
    ManualEntry,
    ManualError,
    allocate_page_labels,
    insert_game,
    load_manual,
    manual_from_data,
    write_manual,
)


class ManualTests(unittest.TestCase):
    def setUp(self):
        self.manual = Manual(
            1,
            (
                ManualEntry("alpha", ("2", "3")),
                ManualEntry("bravo", ("4", "5")),
            ),
        )

    def test_allocates_two_decimal_pages_in_an_integer_gap(self):
        self.assertEqual(allocate_page_labels("3", "4"), ("3.1", "3.2"))

    def test_repeated_insertions_do_not_change_existing_labels(self):
        first = insert_game(self.manual, "added-first", 1)
        second = insert_game(first, "added-before", 1)

        self.assertEqual(first.entry("added-first").pages, ("3.1", "3.2"))
        self.assertEqual(second.entry("added-first").pages, ("3.1", "3.2"))
        self.assertEqual(second.entry("added-before").pages, ("3.01", "3.02"))
        self.assertEqual(second.entry("bravo").pages, ("4", "5"))

    def test_end_insertion_uses_decimal_labels_after_last_page(self):
        result = insert_game(self.manual, "charlie", 2)

        self.assertEqual(result.entry("charlie").pages, ("5.1", "5.2"))

    def test_manifest_rejects_non_increasing_pages(self):
        with self.assertRaisesRegex(ManualError, "not increasing"):
            manual_from_data(
                {
                    "version": 1,
                    "games": [
                        {"id": "alpha", "pages": ["2", "3"]},
                        {"id": "bravo", "pages": ["2.1", "2.2"]},
                    ],
                },
                require_content=False,
            )

    def test_manifest_rejects_stored_print_mode(self):
        with self.assertRaisesRegex(ManualError, "unknown keys: print_mode"):
            manual_from_data(
                {
                    "version": 1,
                    "print_mode": "color",
                    "games": [],
                },
                require_content=False,
            )

    def test_write_and_load_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manual.yaml"
            write_manual(self.manual, path)
            loaded = load_manual(path, require_content=False)

        self.assertEqual(loaded, self.manual)


if __name__ == "__main__":
    unittest.main()
