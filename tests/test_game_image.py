import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import main as app


class GameImageTests(unittest.TestCase):
    def test_matching_research_id_prefers_exact_id(self):
        with tempfile.TemporaryDirectory() as directory:
            research = Path(directory)
            (research / "jaws-pro-2024.md").touch()
            (research / "jaws-pro-stern-2024.md").touch()

            result = app.matching_research_id(
                "Jaws (Pro) Stern 2024", research
            )

        self.assertEqual(result, "jaws-pro-stern-2024")

    def test_matching_research_id_handles_abbreviations_and_omitted_subtitle(self):
        with tempfile.TemporaryDirectory() as directory:
            research = Path(directory)
            (research / "avengers-infinity-quest-le-stern-2020.md").touch()
            (research / "avengers-infinity-quest-pro-stern-2020.md").touch()
            (research / "captain-fantastic-bally-1977.md").touch()

            limited = app.matching_research_id(
                "Avengers: Infinity Quest (Limited Edition) Stern 2020",
                research,
            )
            captain = app.matching_research_id(
                "Captain Fantastic and the Brown Dirt Cowboy "
                "(Home Edition) Bally 1977",
                research,
            )

        self.assertEqual(limited, "avengers-infinity-quest-le-stern-2020")
        self.assertEqual(captain, "captain-fantastic-bally-1977")

    def test_newest_download_since_ignores_old_and_incomplete_files(self):
        with tempfile.TemporaryDirectory() as directory:
            downloads = Path(directory)
            old = downloads / "old.jpg"
            old.write_bytes(b"old")
            snapshot = app.download_snapshot(downloads)
            (downloads / "partial.crdownload").write_bytes(b"partial")
            new = downloads / "playfield.PNG"
            new.write_bytes(b"new")

            result = app.newest_download_since(snapshot, downloads)

        self.assertEqual(result, new)

    def test_first_game_without_image_uses_list_order_and_research_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            game_list = root / "list_of_games.txt"
            images = root / "images"
            research = root / "research"
            images.mkdir()
            research.mkdir()
            game_list.write_text(
                "Jaws (Pro) Stern 2024\n"
                "Captain Fantastic and the Brown Dirt Cowboy "
                "(Home Edition) Bally 1977\n",
                encoding="utf-8",
            )
            (research / "jaws-pro-stern-2024.md").touch()
            (research / "captain-fantastic-bally-1977.md").touch()
            (images / "jaws-pro-stern-2024.jpg").touch()
            (images / "captain-fantastic-bally-1977-bw.png").touch()

            result = app.first_game_without_image(
                game_list,
                images,
                research,
            )

        self.assertEqual(
            result,
            "Captain Fantastic and the Brown Dirt Cowboy "
            "(Home Edition) Bally 1977",
        )

    def test_first_game_without_image_returns_none_when_all_have_images(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            game_list = root / "list_of_games.txt"
            images = root / "images"
            research = root / "research"
            images.mkdir()
            research.mkdir()
            game_list.write_text("A New Game 2026\n", encoding="utf-8")
            (images / "a-new-game-2026.webp").touch()

            result = app.first_game_without_image(
                game_list,
                images,
                research,
            )

        self.assertIsNone(result)

    def test_interactive_game_image_opens_search_and_copies_download(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            downloads = root / "Downloads"
            images = root / "images"
            research = root / "content" / "research"
            downloads.mkdir()
            research.mkdir(parents=True)
            (research / "jaws-pro-stern-2024.md").touch()
            downloaded = downloads / "downloaded.JPEG"

            def download_image(_game):
                downloaded.write_bytes(b"image data")

            with (
                patch.object(app, "ROOT", root),
                patch.object(app, "DOWNLOADS", downloads),
                patch.object(app, "IMAGES", images),
                patch.object(app, "RESEARCH", research),
                patch.object(
                    app,
                    "open_google_image_search",
                    side_effect=download_image,
                ) as opened,
                patch("builtins.input", return_value=""),
                redirect_stdout(stdout),
                redirect_stderr(stderr),
            ):
                result = app.interactive_game_image("Jaws (Pro) Stern 2024")

            destination = images / "jaws-pro-stern-2024.jpeg"
            self.assertEqual(destination.read_bytes(), b"image data")

        self.assertEqual(result, 0)
        opened.assert_called_once_with("Jaws (Pro) Stern 2024")
        self.assertIn("research ID", stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")

    def test_interactive_game_image_derives_id_without_research(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            downloads = root / "Downloads"
            images = root / "images"
            research = root / "research"
            downloads.mkdir()
            research.mkdir()

            def download_image(_game):
                (downloads / "result.webp").write_bytes(b"image data")

            with (
                patch.object(app, "ROOT", root),
                patch.object(app, "DOWNLOADS", downloads),
                patch.object(app, "IMAGES", images),
                patch.object(app, "RESEARCH", research),
                patch.object(
                    app,
                    "open_google_image_search",
                    side_effect=download_image,
                ),
                patch("builtins.input", return_value=""),
                redirect_stdout(io.StringIO()),
            ):
                result = app.interactive_game_image("A New Game 2026")

            self.assertEqual(
                (images / "a-new-game-2026.webp").read_bytes(),
                b"image data",
            )

        self.assertEqual(result, 0)

    def test_interactive_game_image_selects_first_missing_game_when_omitted(self):
        stdout = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            downloads = root / "Downloads"
            images = root / "images"
            research = root / "research"
            game_list = root / "list_of_games.txt"
            downloads.mkdir()
            images.mkdir()
            research.mkdir()
            game_list.write_text(
                "Existing Game 2025\nMissing Game 2026\n",
                encoding="utf-8",
            )
            (images / "existing-game-2025.jpg").touch()

            def download_image(_game):
                (downloads / "result.jpg").write_bytes(b"image data")

            with (
                patch.object(app, "ROOT", root),
                patch.object(app, "DOWNLOADS", downloads),
                patch.object(app, "IMAGES", images),
                patch.object(app, "RESEARCH", research),
                patch.object(app, "GAME_LIST", game_list),
                patch.object(
                    app,
                    "open_google_image_search",
                    side_effect=download_image,
                ) as opened,
                patch("builtins.input", return_value=""),
                redirect_stdout(stdout),
            ):
                result = app.interactive_game_image("")

            self.assertEqual(
                (images / "missing-game-2026.jpg").read_bytes(),
                b"image data",
            )

        self.assertEqual(result, 0)
        opened.assert_called_once_with("Missing Game 2026")
        self.assertIn("Selected first game without an image", stdout.getvalue())

    def test_google_image_search_url_encodes_the_game_name(self):
        url = app.google_image_search_url("AC/DC (Pro) Stern 2012")

        self.assertEqual(
            url,
            "https://www.google.com/search?tbm=isch&q=AC%2FDC+%28Pro%29+Stern+2012",
        )


if __name__ == "__main__":
    unittest.main()
