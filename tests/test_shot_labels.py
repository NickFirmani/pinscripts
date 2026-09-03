import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from PIL import Image

import main as cli
from pinscripts.pdf import _prepare_print_image
import pinscripts.shot_labels as app


class ShotLabelTests(unittest.TestCase):
    def make_game(self, root, color="navy"):
        images = root / "images"
        content = root / "content"
        images.mkdir()
        content.mkdir()
        labels = content / "shot-labels"
        image_path = images / "test-game.webp"
        Image.new("RGB", (400, 700), color).save(image_path, "WEBP", lossless=True)
        data = {
            "id": "test-game",
            "name": "Test Game",
            "image": "images/test-game.webp",
            "shots": [
                {
                    "diagram": 1,
                    "name": "Left orbit",
                    "value": "Builds the mode.",
                    "risk": "Medium",
                },
                {
                    "diagram": 2,
                    "name": "Right ramp",
                    "value": "Collects the jackpot.",
                    "risk": "High",
                },
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
        self.assertEqual(loaded["skipped_diagrams"], [])
        self.assertNotIn("version", loaded)
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

    def test_multiple_coordinates_can_share_one_shot_number(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data, _content, image_path, labels = self.make_game(root)
            coordinates = [
                {"diagram": 1, "x": 75, "y": 180},
                {"diagram": 1, "x": 125, "y": 180},
                {"diagram": 2, "x": 320, "y": 260},
            ]

            app.write_shot_labels(data, image_path, coordinates, labels)

            self.assertEqual(
                app.load_shot_labels(data, root)["coordinates"],
                coordinates,
            )

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

    def test_editor_shows_details_and_can_add_another_label(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data, _content, image_path, labels = self.make_game(root)
            session = app._LabelSession(data, image_path, labels)

            first = session.state()["active_shot"]
            self.assertEqual(first["description"], "Builds the mode.")
            self.assertEqual(first["difficulty"], "Medium")

            session.place(75, 180)
            self.assertEqual(session.state()["active_shot"]["diagram"], 2)
            session.add_another()
            self.assertTrue(session.state()["placing_extra"])
            self.assertEqual(session.state()["active_shot"]["diagram"], 1)
            session.place(125, 180)
            session.place(320, 260)

            self.assertTrue(session.state()["complete"])
            self.assertEqual(
                [point["diagram"] for point in session.coordinates],
                [1, 1, 2],
            )

    def test_editor_can_skip_a_label_and_save_the_decision(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data, _content, image_path, labels = self.make_game(root)
            session = app._LabelSession(data, image_path, labels)

            session.skip_label()
            self.assertEqual(session.state()["active_shot"]["diagram"], 2)
            self.assertEqual(session.state()["skipped_label_count"], 1)
            session.place(320, 260)
            session.save()

            loaded = app.load_shot_labels(data, root)

        self.assertEqual(loaded["skipped_diagrams"], [1])
        self.assertEqual(
            loaded["coordinates"],
            [{"diagram": 2, "x": 320, "y": 260}],
        )

    def test_back_undoes_a_skipped_label(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data, _content, image_path, labels = self.make_game(root)
            session = app._LabelSession(data, image_path, labels)
            session.skip_label()

            session.back()

            state = session.state()
            self.assertEqual(state["active_shot"]["diagram"], 1)
            self.assertEqual(state["shots_placed"], 0)
            self.assertEqual(state["skipped_label_count"], 0)

    def test_save_loads_the_next_unlabelled_game(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, _content, first_image, labels = self.make_game(root)
            second_image = root / "images" / "second-game.webp"
            Image.new("RGB", (400, 700), "green").save(
                second_image,
                "WEBP",
                lossless=True,
            )
            second = {
                **first,
                "id": "second-game",
                "name": "Second Game",
                "image": "images/second-game.webp",
            }
            session = app._LabelSession(
                first,
                first_image,
                labels,
                next_game_loader=lambda: (second, second_image, "labels missing"),
            )
            session.place(75, 180)
            session.place(320, 260)

            session.save()

            state = session.state()
            self.assertEqual(state["game"], "Second Game")
            self.assertEqual(state["shots_placed"], 0)
            self.assertIn("Loaded the next game", state["message"])
            self.assertTrue((labels / "test-game.yaml").is_file())

    def test_skip_discards_placements_and_loads_the_next_game(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, _content, first_image, labels = self.make_game(root)
            second_image = root / "images" / "second-game.webp"
            Image.new("RGB", (400, 700), "green").save(
                second_image,
                "WEBP",
                lossless=True,
            )
            second = {
                **first,
                "id": "second-game",
                "name": "Second Game",
                "image": "images/second-game.webp",
            }
            pending = [(second, second_image, "labels missing")]
            session = app._LabelSession(
                first,
                first_image,
                labels,
                next_game_loader=lambda: pending.pop(0) if pending else None,
            )
            session.place(75, 180)

            session.skip()

            state = session.state()
            self.assertEqual(state["game"], "Second Game")
            self.assertEqual(state["label_count"], 0)
            self.assertIn("Skipped Test Game", state["message"])
            self.assertFalse((labels / "test-game.yaml").exists())
            self.assertEqual(session.skipped_games, ["Test Game"])

    def test_skip_on_last_game_finishes_the_batch_without_saving(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data, _content, image_path, labels = self.make_game(root)
            session = app._LabelSession(data, image_path, labels)

            session.skip()

            self.assertTrue(session.finished.is_set())
            self.assertTrue(session.state()["batch_complete"])
            self.assertFalse((labels / "test-game.yaml").exists())

    def test_page_has_skip_and_closes_the_tab_when_stopped(self):
        page = app._page_html("test-token")

        self.assertIn('id="skip-label">Skip this label', page)
        self.assertIn('id="skip">Skip game', page)
        self.assertIn("window.close()", page)
        self.assertIn("stopEditor", page)

    def test_remaining_loader_selects_the_next_unlabelled_game_in_order(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _first, first_path, _first_image, _labels = self.make_game(root)
            second_image = root / "images" / "second-game.webp"
            Image.new("RGB", (400, 700), "green").save(
                second_image,
                "WEBP",
                lossless=True,
            )
            second = {
                "id": "second-game",
                "name": "Second Game",
                "image": "images/second-game.webp",
                "shots": [
                    {
                        "diagram": 1,
                        "name": "Center ramp",
                        "value": "Starts multiball.",
                        "risk": "Medium",
                    }
                ],
            }
            second_path = root / "content" / "second-game.yaml"
            second_path.write_text(
                yaml.safe_dump(second, sort_keys=False),
                encoding="utf-8",
            )
            loader = app._remaining_game_loader(
                first_path,
                root,
                [first_path, second_path],
            )

            selected, selected_image, issue = loader()

        self.assertEqual(selected["id"], "second-game")
        self.assertEqual(selected_image, second_image)
        self.assertEqual(issue, "shot coordinates are missing")

    def test_print_renderer_scales_labels_for_higher_resolution_variant(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "print.webp"
            Image.new("RGB", (800, 1400), "white").save(
                source,
                "WEBP",
                lossless=True,
            )
            labels = {
                "image_width": 400,
                "image_height": 700,
                "coordinates": [{"diagram": 1, "x": 100, "y": 200}],
            }

            rendered_path = _prepare_print_image(
                source,
                root,
                dpi=1000,
                shot_labels=labels,
            )
            with Image.open(rendered_path) as rendered:
                self.assertNotEqual(rendered.getpixel((220, 400)), (255, 255, 255))

    def test_cli_dispatches_shot_label_editor(self):
        with patch.object(cli, "interactive_shot_labels", return_value=0) as editor:
            result = cli.main(["--shot-labels", "test-game"])

        self.assertEqual(result, 0)
        editor.assert_called_once_with("test-game")


if __name__ == "__main__":
    unittest.main()
