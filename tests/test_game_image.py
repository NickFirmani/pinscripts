import io
import tempfile
import threading
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
                patch.object(app, "image_dimensions", return_value=(1600, 2400)),
                patch.object(app, "first_game_without_image", return_value=None),
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
                patch.object(app, "image_dimensions", return_value=(1600, 2400)),
                patch.object(app, "first_game_without_image", return_value=None),
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
                patch.object(app, "image_dimensions", return_value=(1600, 2400)),
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

    def test_game_image_rejects_low_resolution_download_by_default(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            downloads = root / "Downloads"
            images = root / "images"
            research = root / "research"
            downloads.mkdir()
            research.mkdir()

            def download_image(_game):
                (downloads / "result.jpg").write_bytes(b"low resolution")

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
                patch.object(app, "image_dimensions", return_value=(500, 900)),
                patch("builtins.input", side_effect=["", ""]),
                redirect_stdout(stdout),
                redirect_stderr(stderr),
            ):
                result = app.interactive_game_image("A New Game 2026")

            self.assertFalse((images / "a-new-game-2026.jpg").exists())

        self.assertEqual(result, 0)
        self.assertIn("Downloaded image resolution: 500x900", stdout.getvalue())
        self.assertIn("below 1000px", stderr.getvalue())
        self.assertIn("Image not copied", stderr.getvalue())

    def test_game_image_can_override_low_resolution_warning(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            downloads = root / "Downloads"
            images = root / "images"
            research = root / "research"
            downloads.mkdir()
            research.mkdir()

            def download_image(_game):
                (downloads / "result.jpg").write_bytes(b"rare image")

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
                patch.object(app, "image_dimensions", return_value=(500, 900)),
                patch.object(app, "first_game_without_image", return_value=None),
                patch("builtins.input", side_effect=["", "yes"]),
                redirect_stdout(io.StringIO()),
                redirect_stderr(io.StringIO()),
            ):
                result = app.interactive_game_image("A New Game 2026")

            self.assertEqual(
                (images / "a-new-game-2026.jpg").read_bytes(),
                b"rare image",
            )

        self.assertEqual(result, 0)

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

            def generate_variants(source, output_dir, show_progress=True):
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
                patch("builtins.input", side_effect=["posterize-4", "4"]),
                redirect_stdout(stdout),
            ):
                result = app.interactive_black_and_white_images("")

            self.assertEqual(
                (images / "alpha-bw.png").read_bytes(),
                b"alpha:posterize-4",
            )
            self.assertEqual(
                (images / "beta-bw.png").read_bytes(),
                b"beta:posterize-6",
            )

        self.assertEqual(result, 0)
        self.assertEqual(preview.call_count, 2)
        self.assertIn("Found 2 color image(s)", stdout.getvalue())

    def test_black_and_white_batch_prefetches_next_two_during_review(self):
        sources = [
            Path("/project/images/alpha.jpg"),
            Path("/project/images/beta.jpg"),
            Path("/project/images/gamma.jpg"),
        ]
        started = {
            source: threading.Event()
            for source in sources[1:]
        }
        release_background = threading.Event()

        def generate(source, output_dir, _show_progress):
            if source in started:
                started[source].set()
                release_background.wait(timeout=2)
            return [
                output_dir / f"{source.stem}-{name}.png"
                for name in app.VARIANTS
            ]

        def review(source, _variant_paths):
            if source == sources[0]:
                try:
                    self.assertTrue(started[sources[1]].wait(timeout=2))
                    self.assertTrue(started[sources[2]].wait(timeout=2))
                finally:
                    release_background.set()
            return "skip"

        with (
            patch.object(
                app,
                "generate_black_and_white_variants",
                side_effect=generate,
            ),
            patch.object(
                app,
                "review_black_and_white_variants",
                side_effect=review,
            ) as review_variants,
            redirect_stdout(io.StringIO()),
        ):
            result = app.process_black_and_white_batch(sources)

        self.assertEqual(result, 0)
        self.assertEqual(
            [call.args[0] for call in review_variants.call_args_list],
            sources,
        )

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

    def test_low_resolution_scan_excludes_large_and_black_and_white_images(self):
        with tempfile.TemporaryDirectory() as directory:
            images = Path(directory)
            small = images / "small.jpg"
            large = images / "large.webp"
            narrow_but_long = images / "narrow.png"
            black_and_white = images / "small-bw.png"
            for path in (small, large, narrow_but_long, black_and_white):
                path.touch()

            dimensions = {
                small: (500, 900),
                large: (1200, 1800),
                narrow_but_long: (500, 1200),
            }
            with patch.object(
                app,
                "image_dimensions",
                side_effect=lambda path: dimensions[path],
            ):
                result = app.low_resolution_color_images(images)

        self.assertEqual(result, [(small, 500, 900)])

    def test_low_resolution_repair_searches_for_games_one_at_a_time(self):
        stdout = io.StringIO()
        first = Path("/project/images/alpha.jpg")
        second = Path("/project/images/beta.webp")
        images = [(first, 400, 700), (second, 600, 900)]

        with (
            patch.object(app, "low_resolution_color_images", return_value=images),
            patch.object(app, "open_google_image_search") as opened,
            patch("builtins.input", side_effect=["s", "q"]),
            redirect_stdout(stdout),
        ):
            result = app.interactive_low_resolution_image_repair("")

        self.assertEqual(result, 0)
        self.assertEqual(
            [call.args[0] for call in opened.call_args_list],
            ["alpha", "beta"],
        )
        self.assertIn("[1/2] alpha.jpg (400x700)", stdout.getvalue())
        self.assertIn("[2/2] beta.webp (600x900)", stdout.getvalue())

    def test_low_resolution_repair_resolves_an_explicit_game(self):
        source = Path("/project/images/jaws-pro-stern-2024.jpg")
        with (
            patch.object(app, "find_color_image", return_value=source) as find,
            patch.object(app, "image_dimensions", return_value=(1565, 2560)),
            patch.object(app, "open_google_image_search") as opened,
            patch("builtins.input", return_value="s"),
            redirect_stdout(io.StringIO()),
        ):
            result = app.interactive_low_resolution_image_repair(
                "Jaws (Pro) Stern 2024"
            )

        self.assertEqual(result, 0)
        find.assert_called_once_with("Jaws (Pro) Stern 2024")
        opened.assert_called_once_with("Jaws (Pro) Stern 2024")

    def test_low_resolution_repair_replaces_download_and_reports_improvement(self):
        stdout = io.StringIO()
        source = Path("/project/images/alpha.jpg")
        download = Path("/downloads/better.png")
        backup = Path("/project/images/low-res-backup/alpha.jpg")

        with (
            patch.object(
                app,
                "low_resolution_color_images",
                return_value=[(source, 400, 700)],
            ),
            patch.object(app, "download_snapshot", return_value={}),
            patch.object(app, "newest_download_since", return_value=download),
            patch.object(app, "confirm_image_resolution", return_value=True),
            patch.object(
                app,
                "replace_image_preserving_format",
                return_value=(backup, None),
            ) as replace,
            patch.object(app, "image_dimensions", return_value=(1400, 2400)),
            patch.object(app, "open_google_image_search"),
            patch("builtins.input", return_value=""),
            redirect_stdout(stdout),
        ):
            result = app.interactive_low_resolution_image_repair("")

        self.assertEqual(result, 0)
        replace.assert_called_once_with(download, source)
        self.assertIn("400x700 -> 1400x2400", stdout.getvalue())

    def test_replacement_backs_up_color_and_stale_black_and_white_pair(self):
        with tempfile.TemporaryDirectory() as directory:
            images = Path(directory)
            destination = images / "game.jpg"
            black_and_white = images / "game-bw.png"
            download = images / "download.jpg"
            destination.write_bytes(b"old color")
            black_and_white.write_bytes(b"old bw")
            download.write_bytes(b"new color")

            with patch.object(app, "image_dimensions", return_value=(1600, 2400)):
                backup, black_and_white_backup = (
                    app.replace_image_preserving_format(download, destination)
                )

            self.assertEqual(destination.read_bytes(), b"new color")
            self.assertEqual(backup.read_bytes(), b"old color")
            self.assertFalse(black_and_white.exists())
            self.assertEqual(black_and_white_backup.read_bytes(), b"old bw")

    def test_game_name_for_image_uses_the_original_list_description(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            game_list = root / "list_of_games.txt"
            research = root / "research"
            research.mkdir()
            game_list.write_text(
                "Jaws (Pro) Stern 2024\n",
                encoding="utf-8",
            )
            (research / "jaws-pro-stern-2024.md").touch()

            result = app.game_name_for_image(
                Path("images/jaws-pro-stern-2024.jpg"),
                game_list,
                research,
            )

        self.assertEqual(result, "Jaws (Pro) Stern 2024")

    def test_main_dispatches_low_resolution_image_repair(self):
        with (
            patch.object(
                app,
                "interactive_low_resolution_image_repair",
                return_value=0,
            ) as flow,
            patch(
                "sys.argv",
                ["main.py", "--game-image-low-res", "Jaws (Pro) Stern 2024"],
            ),
        ):
            result = app.main()

        self.assertEqual(result, 0)
        flow.assert_called_once_with("Jaws (Pro) Stern 2024")

    def test_google_image_search_url_encodes_the_game_name(self):
        url = app.google_image_search_url("AC/DC (Pro) Stern 2012")

        self.assertEqual(
            url,
            "https://www.google.com/search?"
            "tbm=isch&q=AC%2FDC+%28Pro%29+Stern+2012+playfield",
        )


if __name__ == "__main__":
    unittest.main()
