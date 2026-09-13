import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pinscripts.binder_workflows as app
from pinscripts.binder import Binder, BinderEntry, BinderSource
from pinscripts.catalog import CatalogGame


class VenueNotesTests(unittest.TestCase):
    def test_notes_are_saved_on_one_binder_entry_and_mark_source_manual(self):
        binder = Binder(
            1,
            "test-binder",
            "Test Binder",
            "printed",
            None,
            BinderSource(
                "pinball-map",
                "25303",
                "https://pinballmap.com/map/?by_location_id=25303",
                "2026-09-13",
            ),
            (BinderEntry("alpha", ("2", "3")),),
        )
        game = CatalogGame("alpha", "Alpha", "Bally", 1980, Path("alpha.yaml"))
        saved = []
        with (
            patch.object(app, "load_binder", return_value=binder),
            patch.object(app, "resolve_game", return_value=game),
            patch("builtins.input", side_effect=["Five balls.", "Extra Balls disabled.", "::end"]),
            patch.object(app, "write_binder", side_effect=lambda value: saved.append(value)),
        ):
            result = app.edit_venue_notes("test-binder", "alpha")

        self.assertEqual(result, 0)
        self.assertEqual(saved[0].entry("alpha").venue_notes, ("Five balls.", "Extra Balls disabled."))
        self.assertEqual(saved[0].source.kind, "manual")
        self.assertEqual(saved[0].source.location_id, "25303")


if __name__ == "__main__":
    unittest.main()
