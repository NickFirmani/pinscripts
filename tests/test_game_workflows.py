import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pinscripts.game_workflows as app
from pinscripts.binder import Binder, BinderEntry, BinderSource, PendingGame
from pinscripts.catalog import CatalogGame


class GameWorkflowTests(unittest.TestCase):
    def test_add_lock_rejects_a_parallel_claim_for_the_same_game(self):
        with tempfile.TemporaryDirectory() as directory:
            locks = Path(directory)
            with app._claim_add_game("alpha", locks) as first:
                with app._claim_add_game("alpha", locks) as second:
                    self.assertTrue(first)
                    self.assertFalse(second)

    def test_parallel_workers_claim_different_pending_games(self):
        pending = tuple(
            PendingGame(name, "Bally", year)
            for name, year in (("Alpha", 1980), ("Bravo", 1981), ("Charlie", 1982))
        )
        binder = Binder(
            2,
            "test-binder",
            "Test Binder",
            "draft",
            None,
            BinderSource("manual"),
            (),
            pending,
        )
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(app, "load_binder", return_value=binder),
                app._claim_next_pending_game("test-binder", directory) as first,
                app._claim_next_pending_game("test-binder", directory) as second,
                app._claim_next_pending_game("test-binder", directory) as third,
            ):
                claimed = {first.key, second.key, third.key}

        self.assertEqual(claimed, {item.key for item in pending})

    def test_pending_completions_merge_into_the_latest_binder(self):
        alpha = PendingGame("Alpha", "Bally", 1980)
        bravo = PendingGame("Bravo", "Bally", 1981)
        current = Binder(
            2,
            "test-binder",
            "Test Binder",
            "draft",
            None,
            BinderSource("pinball-map", "123"),
            (),
            (alpha, bravo),
        )
        catalog = {
            "alpha": CatalogGame("alpha", "Alpha", "Bally", 1980, Path("alpha.yaml")),
            "bravo": CatalogGame("bravo", "Bravo", "Bally", 1981, Path("bravo.yaml")),
        }

        def mutate(_binder_id, mutator):
            nonlocal current
            current = mutator(current)
            return current

        with (
            patch.object(app, "catalog_by_id", return_value=catalog),
            patch.object(app, "mutate_binder", side_effect=mutate),
        ):
            app._finish_pending_game("test-binder", alpha, catalog_id="alpha")
            app._finish_pending_game("test-binder", bravo, catalog_id="bravo")

        self.assertEqual({entry.game_id for entry in current.games}, {"alpha", "bravo"})
        self.assertEqual(current.pending_games, ())

    def test_ignoring_pending_game_saves_a_manual_source_override(self):
        pending = PendingGame("Wrong Game", "Bally", 1980)
        current = Binder(
            2,
            "test-binder",
            "Test Binder",
            "draft",
            None,
            BinderSource("pinball-map", "123"),
            (),
            (pending,),
        )

        def mutate(_binder_id, mutator):
            nonlocal current
            current = mutator(current)
            return current

        with (
            patch.object(app, "catalog_by_id", return_value={}),
            patch.object(app, "mutate_binder", side_effect=mutate),
        ):
            app._finish_pending_game(
                "test-binder",
                pending,
                override_action="ignore",
                reason="Not actually at the venue.",
            )

        self.assertEqual(current.pending_games, ())
        self.assertEqual(current.source.kind, "manual")
        self.assertEqual(current.source_overrides[0].action, "ignore")

    def test_print_mode_defaults_to_color(self):
        with patch("builtins.input", return_value=""):
            self.assertFalse(app.request_print_mode())

    def test_similar_games_are_shown_for_selection_before_add(self):
        candidates = [
            CatalogGame(
                "jaws-pro-stern-2024",
                "JAWS (Pro)",
                "Stern Pinball",
                2024,
                Path("jaws-pro-stern-2024.yaml"),
            ),
            CatalogGame(
                "jaws-prem-le-stern-2024",
                "JAWS (Prem/LE)",
                "Stern Pinball",
                2024,
                Path("jaws-prem-le-stern-2024.yaml"),
            ),
        ]
        with (
            patch.object(app, "similar_catalog_games", return_value=candidates),
            patch("builtins.input", return_value="2"),
        ):
            selected = app._select_similar_game(
                "JAWS (LE)",
                manufacturer="Stern",
                year=2024,
            )

        self.assertEqual(selected.game_id, "jaws-prem-le-stern-2024")

    def test_add_is_catalog_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = root / "content"
            content.mkdir()

            def make_content(_description, research_id=None):
                (content / f"{research_id}.yaml").write_text("id: bravo\n", encoding="utf-8")
                return 0

            with (
                patch.object(app, "CONTENT", content),
                patch.object(app, "ROOT", root),
                patch.object(app, "OUTPUT", root / "output"),
                patch.object(app, "RESEARCH", content / "research"),
                patch.object(app, "_request_new_identity", return_value=("Bravo", "bravo")),
                patch.object(app, "ask_yes_no", return_value=True),
                patch.object(app, "interactive_research_prompt", side_effect=make_content),
                patch.object(app, "_ensure_game_assets", return_value=True),
                patch.object(app, "validate_all", return_value=True),
            ):
                result = app.interactive_add_game("Bravo")

        self.assertEqual(result, 0)

    def test_add_resumes_when_catalog_content_already_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = root / "content"
            content.mkdir()
            (content / "bravo.yaml").write_text(
                "id: bravo\nname: Bravo\n",
                encoding="utf-8",
            )
            with (
                patch.object(app, "CONTENT", content),
                patch.object(app, "ROOT", root),
                patch.object(app, "OUTPUT", root / "output"),
                patch.object(
                    app,
                    "_request_new_identity",
                    return_value=("Bravo", "bravo"),
                ),
                patch.object(app, "interactive_research_prompt") as research,
                patch.object(app, "_ensure_game_assets", return_value=True),
                patch.object(app, "validate_all", return_value=True),
            ):
                first = app.interactive_add_game("Bravo")
                second = app.interactive_add_game("Bravo")

        self.assertEqual((first, second), (0, 0))
        research.assert_not_called()

    def test_asset_check_skips_current_shot_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = root / "content"
            images = root / "images"
            content.mkdir()
            images.mkdir()
            (content / "alpha.yaml").write_text(
                "id: alpha\n",
                encoding="utf-8",
            )
            (images / "alpha.webp").touch()
            with (
                patch.object(app, "CONTENT", content),
                patch.object(app, "ROOT", root),
                patch.object(app, "shot_label_issue", return_value=None),
                patch.object(app, "ask_yes_no") as ask,
                patch.object(app, "interactive_shot_labels") as labels,
            ):
                ready = app._ensure_game_assets(
                    "Alpha",
                    "alpha",
                    False,
                    offer_shot_labels=True,
                )

        self.assertTrue(ready)
        ask.assert_not_called()
        labels.assert_not_called()

    def test_update_builds_a_packet_for_every_printed_binder(self):
        printed = Binder(
            2,
            "printed",
            "Printed",
            "printed",
            None,
            BinderSource("manual"),
            (BinderEntry("alpha", ("2", "3")),),
        )
        draft = Binder(
            2,
            "draft",
            "Draft",
            "draft",
            None,
            BinderSource("manual"),
            (BinderEntry("alpha", ("2", "3")),),
        )
        with tempfile.TemporaryDirectory() as directory:
            content = Path(directory)
            (content / "alpha.yaml").write_text(
                "id: alpha\nname: Alpha\nmetadata: {}\n",
                encoding="utf-8",
            )
            with (
                patch.object(app, "CONTENT", content),
                patch.object(app, "_request_game_id", return_value="alpha"),
                patch("builtins.input", return_value="4"),
                patch.object(app, "validate_game_contexts", return_value=True),
                patch.object(app, "binders_containing", return_value=[printed, draft]),
                patch.object(app, "ask_yes_no", return_value=True),
                patch.object(app, "request_print_mode", return_value=False),
                patch.object(app, "_ensure_game_assets", return_value=True),
                patch.object(
                    app,
                    "build_print_packet",
                    return_value=app.ROOT / "packet.pdf",
                ) as packet,
            ):
                result = app.interactive_update_game("alpha")

        self.assertEqual(result, 0)
        packet.assert_called_once_with("alpha", "update", printed, False)

    def test_update_can_recrop_the_current_image_without_a_download(self):
        with tempfile.TemporaryDirectory() as directory:
            content = Path(directory)
            (content / "alpha.yaml").write_text(
                "id: alpha\nname: Alpha\nmetadata: {}\n",
                encoding="utf-8",
            )
            with (
                patch.object(app, "CONTENT", content),
                patch.object(app, "_request_game_id", return_value="alpha"),
                patch("builtins.input", side_effect=["2", ""]),
                patch.object(
                    app,
                    "interactive_recrop_game_image",
                    return_value="updated",
                ) as recrop,
                patch.object(app, "interactive_game_image") as download,
                patch.object(app, "ask_yes_no", return_value=False),
                patch.object(app, "_ensure_game_assets", return_value=True),
                patch.object(app, "validate_game_contexts", return_value=True),
                patch.object(app, "binders_containing", return_value=[]),
            ):
                result = app.interactive_update_game("alpha")

        self.assertEqual(result, 0)
        recrop.assert_called_once_with("alpha")
        download.assert_not_called()


if __name__ == "__main__":
    unittest.main()
