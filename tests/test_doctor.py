import io
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from PIL import Image

import main as cli
import pinscripts.doctor as app
from pinscripts.content import load_yaml
from pinscripts.shot_labels import write_shot_labels


GAME_ID = "playboy-bally-1978"
FIXTURE = Path(__file__).parents[1] / "content" / f"{GAME_ID}.yaml"


class DoctorTests(unittest.TestCase):
    def make_project(self, root, image_size=(408, 750), include_bw=False, include_labels=False):
        content = root / "content"
        images = root / "images"
        labels = content / "shot-labels"
        binders = root / "binders"
        for directory in (content, images, labels, binders):
            directory.mkdir(parents=True, exist_ok=True)
        content_path = content / FIXTURE.name
        shutil.copy2(FIXTURE, content_path)
        image_path = images / f"{GAME_ID}.webp"
        Image.new("RGB", image_size, "navy").save(image_path, "WEBP", lossless=True)
        if include_bw:
            Image.new("L", (204, 375), 128).save(
                images / f"{GAME_ID}-bw.webp",
                "WEBP",
                lossless=True,
            )
        if include_labels:
            data = load_yaml(content_path)
            write_shot_labels(
                data,
                image_path,
                [],
                labels,
                skipped_diagrams=[shot["diagram"] for shot in data["shots"]],
            )
        return content, images, labels, binders

    def scan(self, root, **kwargs):
        content, images, labels, binders = self.make_project(root, **kwargs)
        return app.scan_project(
            GAME_ID,
            root=root,
            content_directory=content,
            images_directory=images,
            labels_directory=labels,
            binders_directory=binders,
        )

    def test_scan_reports_low_resolution_missing_bw_and_missing_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            report = self.scan(Path(directory))

        self.assertEqual(
            {issue.code for issue in report.issues},
            {"low-resolution-color", "missing-bw", "shot-labels"},
        )

    def test_scan_accepts_complete_assets_and_different_bw_dimensions(self):
        with tempfile.TemporaryDirectory() as directory:
            report = self.scan(
                Path(directory),
                image_size=(816, 1500),
                include_bw=True,
                include_labels=True,
            )

        self.assertEqual(report.issues, ())

    def test_check_mode_never_offers_repairs(self):
        report = app.DoctorReport(
            (),
            (),
            (
                app.DoctorIssue(
                    "Images",
                    "missing-color",
                    "alpha",
                    "missing image",
                ),
            ),
        )
        with (
            patch.object(app, "scan_project", return_value=report),
            patch.object(app, "_repair_interactively") as repair,
            redirect_stdout(io.StringIO()),
        ):
            result = app.run_doctor(check=True)

        self.assertEqual(result, 1)
        repair.assert_not_called()

    def test_repairs_rescan_before_each_dependent_stage(self):
        def report(code=None):
            issues = () if code is None else (
                app.DoctorIssue("Images", code, GAME_ID, "problem"),
            )
            if code == "shot-labels":
                issues = (app.DoctorIssue("Shot labels", code, GAME_ID, "problem"),)
            return app.DoctorReport((), (), issues)

        initial = report("low-resolution-color")
        with (
            patch.object(app, "_ask", return_value=True),
            patch.object(app, "_repair_games") as repair_games,
            patch.object(
                app,
                "scan_project",
                side_effect=[
                    report("missing-bw"),
                    report("shot-labels"),
                    report(),
                ],
            ) as scan,
        ):
            attempted, final = app._repair_interactively(initial, GAME_ID)

        self.assertTrue(attempted)
        self.assertEqual(final.issues, ())
        self.assertEqual(
            [call.args[0] for call in repair_games.call_args_list],
            [(GAME_ID,), (GAME_ID,), (GAME_ID,)],
        )
        self.assertEqual(scan.call_count, 3)

    def test_cli_dispatches_doctor_scope(self):
        with patch.object(cli, "run_doctor", return_value=0) as doctor:
            result = cli.main(["doctor", "--binder", "test-binder", "--check"])

        self.assertEqual(result, 0)
        doctor.assert_called_once_with(None, "test-binder", check=True)


if __name__ == "__main__":
    unittest.main()
