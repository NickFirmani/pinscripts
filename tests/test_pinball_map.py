import io
import unittest

from pinscripts.pinball_map import (
    PinballMapError,
    fetch_location,
    location_id_from_value,
    parse_machine_lines,
    parse_machines_html,
)


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()


class PinballMapTests(unittest.TestCase):
    def test_location_id_accepts_an_id_or_map_url(self):
        self.assertEqual(location_id_from_value("25303"), "25303")
        self.assertEqual(
            location_id_from_value("https://pinballmap.com/map/?by_location_id=25303"),
            "25303",
        )

    def test_machine_html_extracts_name_manufacturer_and_year(self):
        html = """
        <div class="machine_lmx"><div class="machine_name">
          The Addams Family <span class="machine_year_man"> (Bally, 1992)</span>
        </div></div>
        <div class="machine_lmx"><div class="machine_name">
          JAWS (LE) <span class="machine_year_man"> (Stern, 2024)</span>
        </div></div>
        """
        games = parse_machines_html(html)

        self.assertEqual(games[0].name, "The Addams Family")
        self.assertEqual(games[0].manufacturer, "Bally")
        self.assertEqual(games[0].year, 1992)
        self.assertEqual(games[1].name, "JAWS (LE)")

    def test_pasted_lines_use_the_same_strict_format(self):
        games = parse_machine_lines(["The Addams Family (Bally, 1992)"])
        self.assertEqual(games[0].description, "The Addams Family (Bally, 1992)")
        with self.assertRaises(PinballMapError):
            parse_machine_lines(["The Addams Family"])

    def test_fetch_uses_public_html_endpoints_without_an_api_token(self):
        responses = iter(
            [
                b'<div class="location_name">Example Arcade</div>',
                b'<div class="machine_name">Example Game <span> (Bally, 1980)</span></div>',
            ]
        )
        urls = []

        def opener(request, timeout):
            urls.append(request.full_url)
            self.assertEqual(timeout, 20)
            self.assertNotIn("api_token", request.full_url)
            return _Response(next(responses))

        location = fetch_location("25303", opener=opener)

        self.assertEqual(location.name, "Example Arcade")
        self.assertEqual(location.games[0].name, "Example Game")
        self.assertIn("/render_machines", urls[1])


if __name__ == "__main__":
    unittest.main()
