import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from PIL import Image

import main as cli
import pinscripts.shot_labels as app


class ShotLabelTests(unittest.TestCase):
    def make_game(self, root, color="navy"):
        images = root / "images"
        content = root / "content"
        labels = root / "shot-labels"
        images.mkdir()
        content.mkdir()
        image_path = images / "test-game.webp"
        Image.new("RGB", (400, 700), color).save(image_path, "WEBP", lossless=True)
        data = {
            "id": "test-game",
            "name": "Test Game",
            "image": "images/test-game.webp",
            "shots": [
                {"diagram": 1, "name": "Left orbit"},
                {"diagram": 2, "name": "Right ramp"},
            ],
        }
        content_path = content / "test-game.yaml"
        content_path.write_text(
            yaml.safe_dump(data, sort_keys=False),
            encoding="utf-8",
        )
        return data, content_path, image_path, labels

    def test_round_trip_records_coordinates_size_and_fingerprint(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data, _content, image_path, labels = self.make_game(root)
            coordinates = [
                {"diagram": 1, "x": 75, "y": 180},
                {"diagram": 2, "x": 320, "y": 260},
            ]

            destination = app.write_shot_labels(
                data,
                image_path,
                coordinates,
                labels,
            )
            loaded = app.load_shot_labels(data, root)

        self.assertEqual(destination.name, "test-game.yaml")
        self.assertEqual(loaded["image_width"], 400)
        self.assertEqual(loaded["image_height"], 700)
        self.assertEqual(loaded["coordinates"], coordinates)
        self.assertEqual(len(loaded["image_sha256"]), 64)
        self.assertEqual(len(loaded["shots_sha256"]), 64)

    def test_same_size_image_replacement_still_invalidates_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data, _content, image_path, labels = self.make_game(root)
            app.write_shot_labels(
                data,
                image_path,
                [
                    {"diagram": 1, "x": 75, "y": 180},
                    {"diagram": 2, "x": 320, "y": 260},
                ],
                labels,
            )
            Image.new("RGB", (400, 700), "maroon").save(
                image_path,
                "WEBP",
                lossless=True,
            )

            with self.assertRaisesRegex(app.ShotLabelError, "contents changed"):
                app.load_shot_labels(data, root)

    def test_changed_shot_order_invalidates_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data, _content, image_path, labels = self.make_game(root)
            app.write_shot_labels(
                data,
                image_path,
                [
                    {"diagram": 1, "x": 75, "y": 180},
                    {"diagram": 2, "x": 320, "y": 260},
                ],
                labels,
            )
            data["shots"].reverse()

            with self.assertRaisesRegex(app.ShotLabelError, "shot list"):
                app.load_shot_labels(data, root)

    def test_changed_shot_name_invalidates_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data, _content, image_path, labels = self.make_game(root)
            app.write_shot_labels(
                data,
                image_path,
                [
                    {"diagram": 1, "x": 75, "y": 180},
                    {"diagram": 2, "x": 320, "y": 260},
                ],
                labels,
            )
            data["shots"][0]["name"] = "A different physical shot"

            with self.assertRaisesRegex(app.ShotLabelError, "shot list"):
                app.load_shot_labels(data, root)

    def test_first_game_needing_labels_skips_current_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data, content_path, image_path, labels = self.make_game(root)

            selected, issue = app.first_game_needing_labels(
                [content_path],
                root,
                labels,
            )
            self.assertEqual(selected, content_path)
            self.assertEqual(issue, "shot coordinates are missing")

            app.write_shot_labels(
                data,
                image_path,
                [
                    {"diagram": 1, "x": 75, "y": 180},
                    {"diagram": 2, "x": 320, "y": 260},
                ],
                labels,
            )
            selected, issue = app.first_game_needing_labels(
                [content_path],
                root,
                labels,
            )

        self.assertIsNone(selected)
        self.assertIsNone(issue)

    def test_marker_renderer_changes_the_clicked_location(self):
        source = Image.new("RGB", (400, 700), "white")

        rendered = app.draw_shot_labels(
            source,
            [{"diagram": 1, "x": 200, "y": 350}],
        )

        self.assertNotEqual(rendered.getpixel((210, 350)), (255, 255, 255))
        self.assertEqual(source.getpixel((200, 350)), (255, 255, 255))

    def test_cli_dispatches_shot_label_editor(self):
        with patch.object(cli, "interactive_shot_labels", return_value=0) as editor:
            result = cli.main(["--shot-labels", "test-game"])

        self.assertEqual(result, 0)
        editor.assert_called_once_with("test-game")


if __name__ == "__main__":
    unittest.main()
