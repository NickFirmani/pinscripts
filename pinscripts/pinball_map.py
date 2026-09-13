"""Small, unauthenticated HTML reader for Pinball Map location lineups."""

from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
import re
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen


PINBALL_MAP_HOSTS = {"pinballmap.com", "www.pinballmap.com"}
LOCATION_ID_PATTERN = re.compile(r"[1-9][0-9]*")
MACHINE_TEXT_PATTERN = re.compile(r"^\s*(.+)\s+\(([^(),]+),\s*([0-9]{4})\)\s*$")


class PinballMapError(ValueError):
    """Raised when a public Pinball Map listing cannot be read."""


@dataclass(frozen=True)
class ImportedGame:
    name: str
    manufacturer: str
    year: int

    @property
    def description(self):
        return f"{self.name} ({self.manufacturer}, {self.year})"


@dataclass(frozen=True)
class ImportedLocation:
    location_id: str | None
    name: str | None
    url: str | None
    retrieved_at: str
    games: tuple[ImportedGame, ...]


def location_id_from_value(value):
    value = str(value).strip()
    if LOCATION_ID_PATTERN.fullmatch(value):
        return value
    parsed = urlparse(value)
    if parsed.hostname not in PINBALL_MAP_HOSTS:
        raise PinballMapError("expected a Pinball Map URL or numeric location ID")
    query = parse_qs(parsed.query)
    candidates = query.get("by_location_id", []) + query.get("by_location_id[]", [])
    if len(candidates) != 1 or LOCATION_ID_PATTERN.fullmatch(candidates[0]) is None:
        raise PinballMapError("Pinball Map URL has no unambiguous by_location_id")
    return candidates[0]


def canonical_location_url(location_id):
    return f"https://pinballmap.com/map/?by_location_id={location_id}"


class _MachineParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.capture_depth = None
        self.parts = []
        self.rows = []

    def handle_starttag(self, tag, attrs):
        self.depth += 1
        classes = dict(attrs).get("class", "").split()
        if tag == "div" and "machine_name" in classes and self.capture_depth is None:
            self.capture_depth = self.depth
            self.parts = []

    def handle_data(self, data):
        if self.capture_depth is not None:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == "div" and self.capture_depth == self.depth:
            text = " ".join(" ".join(self.parts).split())
            if text:
                self.rows.append(text)
            self.capture_depth = None
            self.parts = []
        self.depth -= 1


class _LocationNameParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.capture_depth = None
        self.parts = []
        self.name = None

    def handle_starttag(self, tag, attrs):
        self.depth += 1
        classes = dict(attrs).get("class", "").split()
        if tag == "div" and "location_name" in classes and self.capture_depth is None:
            self.capture_depth = self.depth

    def handle_data(self, data):
        if self.capture_depth is not None:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == "div" and self.capture_depth == self.depth:
            self.name = " ".join(" ".join(self.parts).split()) or None
            self.capture_depth = None
        self.depth -= 1


def parse_machine_lines(lines):
    games = []
    for line_number, line in enumerate(lines, start=1):
        line = line.strip()
        if not line:
            continue
        match = MACHINE_TEXT_PATTERN.fullmatch(line)
        if match is None:
            raise PinballMapError(
                f"line {line_number} must look like Game Name (Manufacturer, 2024): {line!r}"
            )
        games.append(ImportedGame(match.group(1), match.group(2), int(match.group(3))))
    if not games:
        raise PinballMapError("the listing contains no games")
    descriptions = [game.description.casefold() for game in games]
    if len(set(descriptions)) != len(descriptions):
        raise PinballMapError("the listing contains duplicate games")
    return tuple(games)


def parse_machines_html(text):
    parser = _MachineParser()
    parser.feed(text)
    return parse_machine_lines(parser.rows)


def parse_location_html(text):
    parser = _LocationNameParser()
    parser.feed(text)
    return parser.name


def _get_text(url, opener=urlopen):
    request = Request(
        url,
        headers={
            "User-Agent": "pinscripts/1.0 (personal printable binder importer)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    try:
        with opener(request, timeout=20) as response:
            return response.read().decode("utf-8")
    except (HTTPError, URLError, OSError, UnicodeDecodeError) as error:
        raise PinballMapError(f"could not fetch {url}: {error}") from error


def fetch_location(value, opener=urlopen):
    location_id = location_id_from_value(value)
    location_url = canonical_location_url(location_id)
    detail_url = f"https://pinballmap.com/locations?by_location_id%5B%5D={location_id}&sort=name"
    machines_url = f"https://pinballmap.com/locations/{location_id}/render_machines?sort=alphabetical"
    name = parse_location_html(_get_text(detail_url, opener))
    games = parse_machines_html(_get_text(machines_url, opener))
    return ImportedLocation(
        location_id, name, location_url, date.today().isoformat(), games
    )


def pasted_location(text, name=None):
    return ImportedLocation(None, name, None, date.today().isoformat(), parse_machine_lines(text.splitlines()))
