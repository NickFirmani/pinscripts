import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import yaml

import pinscripts.stern_updates as app
from pinscripts.catalog import CatalogGame


def stern_page(posts):
    payload = json.dumps({"posts": posts})
    return f'<html><script type="application/json" id="bbg-common-env">{payload}</script></html>'


def release_post(title, date="10/12/26", url="https://wp.sternpinball.com/notes.txt"):
    return {
        "title": title,
        "date": date,
        "download_type": "file",
        "download_file": url,
    }


class SternUpdateTests(unittest.TestCase):
    def test_parse_stern_releases_uses_read_me_posts(self):
        page = stern_page(
            [
                release_post("Fallout Pro 0.81.0 Game Code Read Me"),
                {
                    "title": "Fallout Pro 0.81.0 Game Code",
                    "date": "10/12/26",
                    "download_link": "https://example.invalid/code.zip",
                },
            ]
        )

        releases = app.parse_stern_releases(page)

        self.assertEqual(len(releases), 1)
        self.assertEqual(releases[0].name, "Fallout Pro")
        self.assertEqual(releases[0].version, "0.81.0")
        self.assertEqual(releases[0].release_date, "2026-10-12")

    def test_version_comparison_normalizes_prefixes_and_missing_patch(self):
        self.assertEqual(app.version_key("LE v1.02"), app.version_key("1.2.0"))
        self.assertLess(app.version_key("v0.90"), app.version_key("0.95.0"))

    def test_latest_release_matches_premium_to_local_prem_le(self):
        game = CatalogGame(
            "jaws-prem-le-stern-2024",
            "JAWS (Prem/LE)",
            "Stern Pinball",
            2024,
            Path("unused.yaml"),
        )
        releases = [
            app.SternRelease("JAWS Premium", "1.04.0", "2026-10-01", "https://wp.sternpinball.com/prem.txt"),
            app.SternRelease("JAWS Pro", "1.05.0", "2026-10-02", "https://wp.sternpinball.com/pro.txt"),
        ]

        result = app.latest_release_for_game(game, releases)

        self.assertEqual(result.version, "1.04.0")

    def test_release_notes_only_include_versions_newer_than_local(self):
        notes = (
            "PRO V1.03 - October 1, 2026\n*** FIXED ***\n- Latest fix.\n\n"
            "PRO V1.02 - September 1, 2026\n*** NEW ***\n- Already local.\n\n"
            "PRO V1.01 - August 1, 2026\n*** FIXED ***\n- Old fix.\n"
        )

        result = app.release_notes_since(notes, "v1.02.0", "1.03.0")

        self.assertIn("Latest fix", result)
        self.assertNotIn("Already local", result)
        self.assertNotIn("Old fix", result)

    def test_short_fix_only_notes_are_minor(self):
        notes = "PRO V1.03 - October 1, 2026\n*** FIXED ***\n- Fixed a crash.\n- Fixed a typo."

        self.assertFalse(app.substantial_release_notes(notes))
        self.assertEqual(
            app.summarize_release_notes(notes),
            ("Fixed a crash.", "Fixed a typo."),
        )

    def test_new_gameplay_is_substantial_even_when_short(self):
        notes = "PRO V1.03 - October 1, 2026\n*** NEW ***\n- Added a wizard mode."

        self.assertTrue(app.substantial_release_notes(notes))

    def test_short_gameplay_change_is_substantial_without_new_heading(self):
        notes = (
            "PRO V1.03 - October 1, 2026\n*** FIXED ***\n"
            "- Added Top of the Charts challenge as a default game mode option."
        )

        self.assertTrue(app.substantial_release_notes(notes))

    def test_system_menu_additions_remain_minor(self):
        notes = (
            "PRO V1.03 - October 1, 2026\n*** MOVED TO SYSTEM 4.28 ***\n"
            "- Added support for Service Menu diagnostic tests.\n"
            "- Updated nodeboard firmware."
        )

        self.assertFalse(app.substantial_release_notes(notes))

    def test_summary_does_not_append_the_next_version_header(self):
        notes = (
            "PRO V1.03 - October 1, 2026\n*** FIXED ***\n- Fixed a crash.\n"
            "PRO V1.02 - September 1, 2026\n*** FIXED ***\n- Fixed a typo."
        )

        self.assertEqual(
            app.summarize_release_notes(notes),
            ("Fixed a crash.", "Fixed a typo."),
        )

    def test_summary_ignores_decorative_banner_lines(self):
        notes = (
            "*                                                                        *\n"
            "- -----------------------------\n"
            "*** NEW ***\n"
            "- Added a wizard mode."
        )

        self.assertEqual(
            app.summarize_release_notes(notes),
            ("Added a wizard mode.",),
        )

    def test_discovery_compares_local_stern_code_and_fetches_notes(self):
        with tempfile.TemporaryDirectory() as directory:
            content = Path(directory)
            (content / "fallout-pro-stern-2026.yaml").write_text(
                yaml.safe_dump(
                    {
                        "id": "fallout-pro-stern-2026",
                        "name": "Fallout Pro",
                        "metadata": {"manufacturer": "Stern", "year": 2026},
                        "rules_basis": {
                            "kind": "code",
                            "version": "v0.80",
                            "release_date": "2026-09-04",
                        },
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            page = stern_page(
                [release_post("Fallout Pro 0.81.0 Game Code Read Me")]
            )
            notes = "PRO V0.81 - October 12, 2026\n*** FIXED ***\n- Fixed a crash."

            updates = app.discover_stern_updates(
                page,
                fetcher=lambda _url: notes,
                content_directory=content,
            )

        self.assertEqual(len(updates), 1)
        self.assertEqual(updates[0].game_id, "fallout-pro-stern-2026")
        self.assertFalse(updates[0].substantial)

    def test_short_update_skip_is_recorded(self):
        update = app.SternUpdate(
            "fallout-pro-stern-2026",
            "Fallout Pro",
            "0.80",
            app.SternRelease(
                "Fallout Pro",
                "0.81.0",
                "2026-10-12",
                "https://wp.sternpinball.com/notes.txt",
            ),
            "*** FIXED ***\n- Fixed a crash.",
            ("Fixed a crash.",),
            False,
        )
        page = stern_page([release_post("Fallout Pro 0.81.0 Game Code Read Me")])

        with tempfile.TemporaryDirectory() as directory:
            content = Path(directory)
            path = content / f"{update.game_id}.yaml"
            path.write_text(
                yaml.safe_dump(
                    {
                        "id": update.game_id,
                        "name": update.game_name,
                        "metadata": {"manufacturer": "Stern", "year": 2026},
                        "rules_basis": {
                            "kind": "code",
                            "version": "0.80",
                            "release_date": "2026-09-04",
                        },
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            with (
                patch.object(app, "discover_stern_updates", return_value=[update]),
                patch.object(app, "ask_yes_no", return_value=False),
                patch.object(app, "_apply_minor_update") as apply_update,
                redirect_stdout(io.StringIO()) as stdout,
            ):
                result = app.check_stern_code_updates(
                    fetcher=lambda _url: page,
                    content_directory=content,
                )
            saved = yaml.safe_load(
                (content / "state" / "stern-code-ignores.yaml").read_text(
                    encoding="utf-8"
                )
            )

        self.assertEqual(result, 0)
        apply_update.assert_not_called()
        self.assertEqual(
            saved[update.game_id],
            {"version": "0.81.0", "release_date": "2026-10-12"},
        )
        self.assertIn("will not ask about it again", stdout.getvalue())

    def test_discovery_suppresses_ignored_version_but_finds_a_newer_one(self):
        with tempfile.TemporaryDirectory() as directory:
            content = Path(directory)
            path = content / "fallout-pro-stern-2026.yaml"
            path.write_text(
                yaml.safe_dump(
                    {
                        "id": "fallout-pro-stern-2026",
                        "name": "Fallout Pro",
                        "metadata": {"manufacturer": "Stern", "year": 2026},
                        "rules_basis": {
                            "kind": "code",
                            "version": "0.80",
                            "release_date": "2026-09-04",
                        },
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            state = content / "state"
            state.mkdir()
            (state / "stern-code-ignores.yaml").write_text(
                yaml.safe_dump(
                    {
                        "fallout-pro-stern-2026": {
                            "version": "0.81.0",
                            "release_date": "2026-10-12",
                        }
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            ignored_page = stern_page(
                [release_post("Fallout Pro 0.81.0 Game Code Read Me")]
            )
            self.assertEqual(
                app.discover_stern_updates(
                    ignored_page,
                    fetcher=lambda _url: "unused",
                    content_directory=content,
                ),
                [],
            )

            newer_page = stern_page(
                [release_post("Fallout Pro 0.82.0 Game Code Read Me")]
            )
            notes = (
                "PRO V0.82 - October 18, 2026\n*** FIXED ***\n- New fix.\n\n"
                "PRO V0.81 - October 12, 2026\n*** FIXED ***\n- Ignored fix."
            )
            updates = app.discover_stern_updates(
                newer_page,
                fetcher=lambda _url: notes,
                content_directory=content,
            )

        self.assertEqual(len(updates), 1)
        self.assertEqual(updates[0].summary, ("New fix.",))
        self.assertNotIn("Ignored fix", updates[0].notes)

    def test_minor_update_writes_version_then_runs_packet_flow(self):
        update = app.SternUpdate(
            "fallout-pro-stern-2026",
            "Fallout Pro",
            "0.80",
            app.SternRelease(
                "Fallout Pro",
                "0.81.0",
                "2026-10-12",
                "https://wp.sternpinball.com/notes.txt",
            ),
            "*** FIXED ***\n- Fixed a crash.",
            ("Fixed a crash.",),
            False,
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = root / "content"
            content.mkdir()
            path = content / "fallout-pro-stern-2026.yaml"
            path.write_text(
                yaml.safe_dump(
                    {
                        "id": update.game_id,
                        "name": update.game_name,
                        "metadata": {"manufacturer": "Stern", "year": 2026},
                        "rules_basis": {
                            "kind": "code",
                            "version": "0.80",
                            "release_date": "2026-09-04",
                        },
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            with (
                patch.object(app, "CONTENT", content),
                patch.object(app, "ROOT", root),
                patch.object(app, "validate_game_contexts", return_value=True),
                patch.object(app, "_update_description", return_value="Fallout Pro"),
                patch.object(
                    app,
                    "_validate_and_offer_update_packets",
                    return_value=0,
                ) as packets,
                redirect_stdout(io.StringIO()),
            ):
                result = app._apply_minor_update(update)

            saved = yaml.safe_load(path.read_text(encoding="utf-8"))

        self.assertEqual(result, 0)
        self.assertEqual(saved["rules_basis"]["version"], "0.81.0")
        self.assertEqual(saved["rules_basis"]["release_date"], "2026-10-12")
        packets.assert_called_once_with(update.game_id, "Fallout Pro", True)

    def test_substantial_update_starts_research_without_extra_confirmation(self):
        update = app.SternUpdate(
            "fallout-pro-stern-2026",
            "Fallout Pro",
            "0.80",
            app.SternRelease(
                "Fallout Pro",
                "0.81.0",
                "2026-10-12",
                "https://wp.sternpinball.com/notes.txt",
            ),
            "*** NEW ***\n- Added a mode.",
            ("Added a mode.",),
            True,
        )
        page = stern_page([release_post("Fallout Pro 0.81.0 Game Code Read Me")])

        with (
            patch.object(app, "discover_stern_updates", return_value=[update]),
            patch.object(app, "_apply_substantial_update", return_value=0) as apply_update,
            patch.object(app, "ask_yes_no") as confirm,
            redirect_stdout(io.StringIO()),
        ):
            result = app.check_stern_code_updates(fetcher=lambda _url: page)

        self.assertEqual(result, 0)
        apply_update.assert_called_once_with(update)
        confirm.assert_not_called()

    def test_substantial_update_refreshes_changed_shot_labels_before_packets(self):
        update = app.SternUpdate(
            "fallout-pro-stern-2026",
            "Fallout Pro",
            "0.80",
            app.SternRelease(
                "Fallout Pro",
                "0.81.0",
                "2026-10-12",
                "https://wp.sternpinball.com/notes.txt",
            ),
            "*** NEW ***\n- Added a mode.",
            ("Added a mode.",),
            True,
        )
        with (
            patch.object(app, "_update_description", return_value="Fallout Pro"),
            patch.object(app, "_refresh_content_with_review", return_value=True) as refresh,
            patch.object(app, "load_yaml", return_value={"id": update.game_id}),
            patch.object(app, "shot_label_issue", return_value="shot list changed"),
            patch.object(app, "interactive_shot_labels", return_value=0) as labels,
            patch.object(
                app,
                "_validate_and_offer_update_packets",
                return_value=0,
            ) as packets,
            redirect_stdout(io.StringIO()),
        ):
            result = app._apply_substantial_update(update)

        self.assertEqual(result, 0)
        self.assertTrue(refresh.call_args.kwargs["allow_stale_shot_labels"])
        labels.assert_called_once_with(update.game_id, continue_batch=False)
        packets.assert_called_once()
        self.assertEqual(packets.call_args.args[0], update.game_id)
        self.assertTrue(packets.call_args.args[2])


if __name__ == "__main__":
    unittest.main()
