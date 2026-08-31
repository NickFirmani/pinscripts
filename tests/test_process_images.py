import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main as app
from scripts import process_images as image_processor


class ProcessImagesTests(unittest.TestCase):
    def test_process_images_generates_every_variant(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "playfield.jpg"
            output_dir = root / "variants"
            source.touch()

            with (
                patch.object(
                    image_processor.shutil,
                    "which",
                    return_value="/usr/bin/magick",
                ),
                patch.object(image_processor, "run_variant") as run_variant,
            ):
                result = image_processor.process_images(source, output_dir)

        self.assertEqual(result, output_dir)
        self.assertEqual(run_variant.call_count, len(image_processor.VARIANTS))
        generated_names = {
            call.args[1].name
            for call in run_variant.call_args_list
        }
        self.assertEqual(
            generated_names,
            {
                f"playfield-{variant}.png"
                for variant in image_processor.VARIANTS
            },
        )

    def test_process_images_reports_missing_imagemagick(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "playfield.jpg"
            source.touch()

            with (
                patch.object(image_processor.shutil, "which", return_value=None),
                self.assertRaisesRegex(
                    SystemExit,
                    "ImageMagick is required.*magick.*not found",
                ),
            ):
                image_processor.process_images(source)

    def test_main_dispatches_process_images_helper(self):
        with (
            patch.object(app, "process_images") as process_images,
            patch(
                "sys.argv",
                [
                    "main.py",
                    "--process-images",
                    "playfield.jpg",
                    "--image-output-dir",
                    "variants",
                ],
            ),
        ):
            result = app.main()

        self.assertEqual(result, 0)
        process_images.assert_called_once_with(
            Path("playfield.jpg"),
            Path("variants"),
        )


if __name__ == "__main__":
    unittest.main()
