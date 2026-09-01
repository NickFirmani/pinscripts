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

    def test_color_images_without_black_and_white_finds_only_unpaired_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            images = Path(directory)
            paired = images / "paired.jpg"
            missing = images / "missing.webp"
            paired.touch()
            missing.touch()
            (images / "paired-bw.png").touch()
            (images / "orphan-bw.png").touch()
            (images / "notes.txt").touch()

            result = app.color_images_without_black_and_white(images)

        self.assertEqual(result, [missing])

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

    def test_black_and_white_flow_processes_every_unpaired_color_image(self):
        stdout = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            images = root / "images"
            images.mkdir()
            first = images / "alpha.jpg"
            second = images / "beta.webp"
            paired = images / "paired.png"
            first.write_bytes(b"alpha color")
            second.write_bytes(b"beta color")
            paired.write_bytes(b"paired color")
            (images / "paired-bw.png").write_bytes(b"paired bw")

            def generate_variants(source, output_dir):
                output_dir.mkdir(parents=True, exist_ok=True)
                for name in app.VARIANTS:
                    (output_dir / f"{source.stem}-{name}.png").write_bytes(
                        f"{source.stem}:{name}".encode()
                    )
                return output_dir

            with (
                patch.object(app, "ROOT", root),
                patch.object(app, "IMAGES", images),
                patch.object(app, "process_images", side_effect=generate_variants),
                patch.object(app, "open_images_in_preview") as preview,
                patch("builtins.input", side_effect=["posterize-4", "8"]),
                redirect_stdout(stdout),
            ):
                result = app.interactive_black_and_white_images("")

            self.assertEqual(
                (images / "alpha-bw.png").read_bytes(),
                b"alpha:posterize-4",
            )
            self.assertEqual(
                (images / "beta-bw.png").read_bytes(),
                b"beta:bw-clean",
            )

        self.assertEqual(result, 0)
        self.assertEqual(preview.call_count, 2)
        self.assertIn("Found 2 color image(s)", stdout.getvalue())

    def test_black_and_white_flow_resolves_an_explicit_game_name(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            images = root / "images"
            research = root / "research"
            images.mkdir()
            research.mkdir()
            source = images / "jaws-pro-stern-2024.jpg"
            source.touch()
            (research / "jaws-pro-stern-2024.md").touch()

            with (
                patch.object(app, "IMAGES", images),
                patch.object(app, "RESEARCH", research),
                patch.object(
                    app,
                    "process_black_and_white_image",
                    return_value="skip",
                ) as process,
            ):
                result = app.interactive_black_and_white_images(
                    "Jaws (Pro) Stern 2024"
                )

        self.assertEqual(result, 0)
        process.assert_called_once_with(source)

    def test_main_dispatches_black_and_white_image_flow(self):
        with (
            patch.object(
                app,
                "interactive_black_and_white_images",
                return_value=0,
            ) as flow,
            patch(
                "sys.argv",
                ["main.py", "--game-image-bw", "Jaws (Pro) Stern 2024"],
            ),
        ):
            result = app.main()

        self.assertEqual(result, 0)
        flow.assert_called_once_with("Jaws (Pro) Stern 2024")

    def test_google_image_search_url_encodes_the_game_name(self):
        url = app.google_image_search_url("AC/DC (Pro) Stern 2012")

        self.assertEqual(
            url,
            "https://www.google.com/search?tbm=isch&q=AC%2FDC+%28Pro%29+Stern+2012",
        )


if __name__ == "__main__":
    unittest.main()
