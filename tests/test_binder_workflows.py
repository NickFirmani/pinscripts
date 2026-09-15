import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pinscripts.binder_workflows as app
from pinscripts.binder import Binder, BinderEntry, BinderSource, PendingGame, SourceOverride
from pinscripts.catalog import CatalogGame, match_imported_game
from pinscripts.pinball_map import ImportedGame, ImportedLocation


class BinderWorkflowTests(unittest.TestCase):
    def test_sync_optionally_runs_the_existing_pending_game_workflow(self):
        pending = PendingGame("Unknown", "Bally", 1981)
        imported = ImportedLocation(
            "123",
            "Test Binder",
            "https://pinballmap.com/map/?by_location_id=123",
            "2026-09-15",
            (),
        )
        for has_pending, accept, population_result in (
            (True, True, 0),
            (True, True, 1),
            (True, False, 0),
            (False, True, 0),
        ):
            with self.subTest(
                has_pending=has_pending,
                accept=accept,
                population_result=population_result,
            ):
                binder = Binder(
                    2,
                    "test-binder",
                    "Test Binder",
                    "draft",
                    None,
                    BinderSource("manual", "123"),
                    (),
                    (pending,) if has_pending else (),
                )
                with (
                    patch.object(app, "load_binder", return_value=binder),
                    patch.object(app, "_load_import", return_value=imported),
                    patch.object(app, "classify_imported", return_value=([], [], [])),
                    patch.object(app, "catalog_by_id", return_value={}),
                    patch.object(app, "write_binder") as write,
                    patch.object(app, "ask_yes_no", return_value=accept) as ask,
                    patch.object(
                        app, "interactive_add_game", return_value=population_result
                    ) as populate,
                ):
                    result = app.sync_binder_interactive("test-binder")

                write.assert_called_once()
                if has_pending:
                    ask.assert_called_once_with(
                        "Would you like to edit/populate the pending games now?",
                        default=True,
                    )
                else:
                    ask.assert_not_called()
                if has_pending and accept:
                    populate.assert_called_once_with(binder_id="test-binder")
                    self.assertEqual(result, population_result)
                else:
                    populate.assert_not_called()
                    self.assertEqual(result, 0)

    def test_add_to_printed_binder_writes_manifest_and_insert_packets(self):
        binder = Binder(
            2,
            "test-binder",
            "Test Binder",
            "printed",
            "2026-09-01",
            BinderSource("manual"),
            (BinderEntry("alpha", ("2", "3")),),
        )
        alpha = CatalogGame("alpha", "Alpha", "Bally", 1980, Path("alpha.yaml"))
        game = CatalogGame("bravo", "Bravo", "Bally", 1981, Path("bravo.yaml"))
        with (
            patch.object(app, "load_binder", return_value=binder),
            patch.object(app, "resolve_game", return_value=game),
            patch.object(app, "catalog_by_id", return_value={"alpha": alpha, "bravo": game}),
            patch.object(app, "write_binder") as write,
            patch.object(app, "build_print_packet", return_value=Path("packet.pdf")) as packet,
        ):
            result = app.add_binder_game("test-binder", "bravo", "both")

        updated = write.call_args.args[0]
        self.assertEqual(result, 0)
        self.assertEqual(updated.entry("bravo").pages, ("3.1", "3.2"))
        self.assertEqual(
            [call.args[3] for call in packet.call_args_list],
            [False, True],
        )
        self.assertTrue(all(call.args[1] == "add" for call in packet.call_args_list))

    def test_readding_existing_printed_game_only_regenerates_insert_packet(self):
        entry = BinderEntry("alpha", ("2", "3"))
        binder = Binder(
            2,
            "test-binder",
            "Test Binder",
            "printed",
            "2026-09-01",
            BinderSource("manual"),
            (entry,),
        )
        game = CatalogGame("alpha", "Alpha", "Bally", 1980, Path("alpha.yaml"))
        with (
            patch.object(app, "load_binder", return_value=binder),
            patch.object(app, "resolve_game", return_value=game),
            patch.object(app, "write_binder") as write,
            patch.object(app, "build_print_packet", return_value=Path("packet.pdf")) as packet,
        ):
            result = app.add_binder_game("test-binder", "alpha")

        self.assertEqual(result, 0)
        write.assert_not_called()
        packet.assert_called_once_with("alpha", "add", binder, False)

    def test_update_printed_binder_writes_replacement_packet_without_mutation(self):
        binder = Binder(
            2,
            "test-binder",
            "Test Binder",
            "printed",
            "2026-09-01",
            BinderSource("manual"),
            (BinderEntry("alpha", ("2", "3")),),
        )
        game = CatalogGame("alpha", "Alpha", "Bally", 1980, Path("alpha.yaml"))
        with (
            patch.object(app, "load_binder", return_value=binder),
            patch.object(app, "resolve_game", return_value=game),
            patch.object(app, "write_binder") as write,
            patch.object(app, "build_print_packet", return_value=Path("packet.pdf")) as packet,
        ):
            result = app.update_binder_game("test-binder", "alpha", "bw")

        self.assertEqual(result, 0)
        write.assert_not_called()
        packet.assert_called_once_with("alpha", "update", binder, True)

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
