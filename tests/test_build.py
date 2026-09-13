import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main as cli
import pinscripts.build as app
from pinscripts.binder import Binder, BinderEntry, BinderSource


class BuildTests(unittest.TestCase):
    def test_catalog_build_discovers_content_without_a_manifest(self):
        paths = [Path("content/alpha.yaml"), Path("content/bravo.yaml")]
        output = Path("/project/output")
        with (
            patch.object(app, "OUTPUT", output),
            patch.object(app, "content_paths", return_value=paths),
            patch.object(app, "validate_all", return_value=True),
            patch.object(app, "render") as render,
            patch.object(app, "merge_pdfs") as merge,
        ):
            result = app.build_catalog(True)

        self.assertEqual(result, 0)
        render.assert_called_once_with(paths, True, None, None)
        merge.assert_called_once_with(
            [output / "alpha-bw.pdf", output / "bravo-bw.pdf"],
            output / "catalog-bw.pdf",
            "Master Catalog",
            None,
        )

    def test_binder_build_applies_pages_and_venue_notes(self):
        binder = Binder(
            2,
            "test-binder",
            "Test Binder",
            "printed",
            None,
            BinderSource("manual"),
            (BinderEntry("alpha", ("19.1", "19.2"), True, ("Local setup.",)),),
        )
        output = Path("/project/output")
        path = app.CONTENT / "alpha.yaml"
        with (
            patch.object(app, "OUTPUT", output),
            patch.object(app, "load_binder", return_value=binder),
            patch.object(app, "validate_all", return_value=True),
            patch.object(app, "render") as render,
            patch.object(app, "merge_pdfs") as merge,
        ):
            result = app.build_binder("test-binder")

        self.assertEqual(result, 0)
        render.assert_called_once_with(
            [path],
            False,
            {"alpha": ("19.1", "19.2")},
            {"alpha": ("Local setup.",)},
        )
        merge.assert_called_once_with(
            [output / "alpha.pdf"],
            output / "binders" / "test-binder.pdf",
            "Test Binder",
            None,
        )

    def test_packet_uses_selected_binder_context(self):
        binder = Binder(
            2,
            "test-binder",
            "Test Binder",
            "printed",
            None,
            BinderSource("manual"),
            (
                BinderEntry("alpha", ("18", "19")),
                BinderEntry("bravo", ("19.1", "19.2"), True, ("Venue note.",)),
                BinderEntry("charlie", ("20", "21")),
            ),
        )
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            with (
                patch.object(app, "OUTPUT", output),
                patch.object(app, "validate_all", return_value=True),
                patch.object(app, "render_game") as render_game,
                patch.object(app, "merge_print_packet"),
            ):
                packet = app.build_print_packet("bravo", "update", binder)

        self.assertEqual(packet, output / "print/test-binder/update-bravo.pdf")
        self.assertEqual(
            [call.kwargs["page_labels"] for call in render_game.call_args_list],
            [("18", "19"), ("19.1", "19.2"), ("20", "21")],
        )
        self.assertEqual(render_game.call_args_list[1].kwargs["venue_notes"], ("Venue note.",))

    def test_cli_dispatches_catalog_and_binder_builds(self):
        with patch.object(cli, "build_catalog", return_value=0) as catalog:
            self.assertEqual(cli.main(["catalog", "build", "--bw"]), 0)
        catalog.assert_called_once_with(True)

        with patch.object(cli, "build_binder", return_value=0) as binder:
            self.assertEqual(cli.main(["binder", "build", "lyons-classic-pinball"]), 0)
        binder.assert_called_once_with("lyons-classic-pinball", False)


if __name__ == "__main__":
    unittest.main()
