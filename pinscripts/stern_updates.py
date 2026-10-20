"""Discover and apply Stern game-code updates from the official support site."""

from dataclasses import dataclass
from datetime import datetime
from html import unescape
import difflib
import json
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import yaml

from .catalog import canonical_game_key, load_catalog
from .build import validate_game_contexts
from .content import load_yaml, normalized_game_id
from .game_workflows import (
    _refresh_content_with_review,
    _update_description,
    _validate_and_offer_update_packets,
    ask_yes_no,
)
from .paths import CONTENT, ROOT
from .shot_labels import interactive_shot_labels, shot_label_issue


STERN_CODE_URL = "https://www.sternpinball.com/support/game-code/"
MAX_RESPONSE_BYTES = 4 * 1024 * 1024
MINOR_MAX_BULLETS = 12
MINOR_MAX_CHARACTERS = 2500

RELEASE_TITLE = re.compile(
    r"^(?P<name>.+?)\s+(?P<version>v?\d+(?:\.\d+){1,2})\s+"
    r"Game Code Read Me$",
    re.IGNORECASE,
)
VERSION_HEADER = re.compile(
    r"^\s*(?:(?:PRO|PREMIUM|LE|PREM(?:IUM)?/LE)\s+)?"
    r"(?:VERSION\s+|V)?(?P<version>\d+(?:\.\d+){1,2})\s*"
    r"(?:-|\u2013)\s*.+$",
    re.IGNORECASE | re.MULTILINE,
)
SUBSTANTIAL_HEADING = re.compile(
    r"\*{2,}\s*(?:NEW|ADDED|NEW RULES?)\b",
    re.IGNORECASE,
)
GAMEPLAY_CHANGE = re.compile(
    r"^\s*[-*]\s+(?:add(?:ed)?|chang(?:e|ed)|tweak(?:ed)?)\b.*\b"
    r"(?:mode|multiball|scor(?:e|ing)|jackpot|wizard|challenge|skill shot|"
    r"ball save|rules?|feature|award|extra ball|playfield shot)\b",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass(frozen=True)
class SternRelease:
    name: str
    version: str
    release_date: str
    notes_url: str


@dataclass(frozen=True)
class SternUpdate:
    game_id: str
    game_name: str
    current_version: str
    release: SternRelease
    notes: str
    summary: tuple[str, ...]
    substantial: bool


def fetch_text(url, timeout=30):
    def is_stern_url(value):
        parsed = urlparse(value)
        return parsed.scheme == "https" and (
            parsed.hostname == "sternpinball.com"
            or (parsed.hostname or "").endswith(".sternpinball.com")
        )

    if not is_stern_url(url):
        raise ValueError(f"refusing non-Stern URL: {url}")
    request = Request(url, headers={"User-Agent": "PinScripts/1.0 code-update-checker"})
    with urlopen(request, timeout=timeout) as response:
        if not is_stern_url(response.geturl()):
            raise ValueError(f"refusing non-Stern redirect: {response.geturl()}")
        payload = response.read(MAX_RESPONSE_BYTES + 1)
        if len(payload) > MAX_RESPONSE_BYTES:
            raise ValueError(f"Stern response is larger than {MAX_RESPONSE_BYTES} bytes")
        charset = response.headers.get_content_charset() or "utf-8"
    return payload.decode(charset, errors="replace")


def version_key(value):
    match = re.search(r"\d+(?:\.\d+)+", str(value))
    if not match:
        return None
    parts = tuple(int(part) for part in match.group().split("."))
    return parts + (0,) * (4 - len(parts))


def _release_date(value):
    return datetime.strptime(value, "%m/%d/%y").date().isoformat()


def parse_stern_releases(page):
    match = re.search(
        r"<script[^>]+id=[\"']bbg-common-env[\"'][^>]*>(?P<data>.*?)</script>",
        page,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if not match:
        raise ValueError("Stern page does not contain the bbg-common-env index")
    try:
        environment = json.loads(unescape(match.group("data")))
    except json.JSONDecodeError as error:
        raise ValueError(f"Stern post index is not valid JSON: {error}") from error

    releases = []
    for post in environment.get("posts", []):
        title_match = RELEASE_TITLE.fullmatch(str(post.get("title", "")).strip())
        notes_url = str(post.get("download_file", "")).strip()
        if not title_match or not notes_url:
            continue
        try:
            release_date = _release_date(str(post.get("date", "")))
        except ValueError:
            continue
        releases.append(
            SternRelease(
                title_match.group("name").strip(),
                title_match.group("version").lstrip("vV"),
                release_date,
                notes_url,
            )
        )
    if not releases:
        raise ValueError("Stern post index contains no game-code release notes")
    return releases


def _release_identity(name):
    title, trim, _manufacturer, _year = canonical_game_key(name, "Stern", None)
    title = re.sub(r"-(?:by-)?stern-pinball$", "", title)
    return title, trim


def _matching_releases(game, releases):
    local_title, local_trim = _release_identity(game.name)
    exact = [
        release
        for release in releases
        if _release_identity(release.name) == (local_title, local_trim)
    ]
    if exact:
        return exact

    candidates = []
    for release in releases:
        release_title, release_trim = _release_identity(release.name)
        if local_trim != release_trim:
            continue
        score = difflib.SequenceMatcher(None, local_title, release_title).ratio()
        if score >= 0.82:
            candidates.append((score, release))
    candidates.sort(key=lambda item: item[0], reverse=True)
    if not candidates:
        return []
    if len(candidates) > 1 and candidates[0][0] - candidates[1][0] < 0.08:
        return []
    best_identity = _release_identity(candidates[0][1].name)
    return [release for release in releases if _release_identity(release.name) == best_identity]


def latest_release_for_game(game, releases):
    candidates = _matching_releases(game, releases)
    usable = [release for release in candidates if version_key(release.version) is not None]
    if not usable:
        return None
    return max(usable, key=lambda release: (version_key(release.version), release.release_date))


def release_notes_since(notes, current_version, latest_version):
    current = version_key(current_version)
    latest = version_key(latest_version)
    if current is None or latest is None or current >= latest:
        return ""
    headers = list(VERSION_HEADER.finditer(notes))
    if not headers:
        return notes.strip()
    sections = []
    for index, header in enumerate(headers):
        section_version = version_key(header.group("version"))
        end = headers[index + 1].start() if index + 1 < len(headers) else len(notes)
        if section_version is not None and current < section_version <= latest:
            sections.append(notes[header.start():end].strip())
    return "\n\n".join(sections)


def summarize_release_notes(notes, limit=10):
    bullets = []
    current = None
    current_indent = None
    for raw_line in notes.splitlines():
        line = raw_line.strip()
        bullet_match = re.match(r"^(?P<indent>\s*)[-*]\s+(?P<text>\S.*)$", raw_line)
        if bullet_match:
            bullet_text = bullet_match.group("text")
            if re.fullmatch(r"[-*_=\s]+", bullet_text):
                current = None
                current_indent = None
                continue
            current = bullet_text
            current_indent = len(bullet_match.group("indent"))
            bullets.append(current)
        elif (
            current
            and line
            and not VERSION_HEADER.match(line)
            and not line.startswith("***")
            and len(raw_line) - len(raw_line.lstrip()) > current_indent
        ):
            bullets[-1] += " " + line
        else:
            current = None
            current_indent = None
    if bullets:
        return tuple(bullets[:limit])
    prose = [
        line.strip()
        for line in notes.splitlines()
        if line.strip()
        and not VERSION_HEADER.match(line)
        and not line.strip().startswith("***")
    ]
    return tuple(prose[:limit])


def substantial_release_notes(notes):
    bullet_count = len(re.findall(r"^\s*[-*]\s+\S", notes, re.MULTILINE))
    return bool(
        SUBSTANTIAL_HEADING.search(notes)
        or GAMEPLAY_CHANGE.search(notes)
        or bullet_count > MINOR_MAX_BULLETS
        or len(notes) > MINOR_MAX_CHARACTERS
    )


def _ignored_updates_path(content_directory):
    return content_directory / "state" / "stern-code-ignores.yaml"


def _load_ignored_updates(content_directory):
    path = _ignored_updates_path(content_directory)
    if not path.exists():
        return {}
    data = load_yaml(path)
    if not isinstance(data, dict):
        raise ValueError(f"Stern code ignore state must be a mapping: {path}")
    for game_id, release in data.items():
        if (
            not isinstance(game_id, str)
            or not isinstance(release, dict)
            or version_key(release.get("version")) is None
            or not isinstance(release.get("release_date"), str)
        ):
            raise ValueError(f"invalid Stern code ignore state for {game_id!r}: {path}")
    return data


def discover_stern_updates(page, fetcher=fetch_text, content_directory=CONTENT):
    releases = parse_stern_releases(page)
    ignored_updates = _load_ignored_updates(content_directory)
    updates = []
    notes_cache = {}
    for game in load_catalog(content_directory):
        if "stern" not in normalized_game_id(game.manufacturer):
            continue
        data = load_yaml(game.path)
        basis = data.get("rules_basis", {})
        if basis.get("kind") != "code" or version_key(basis.get("version")) is None:
            continue
        release = latest_release_for_game(game, releases)
        current_version = str(basis["version"])
        if release is None or version_key(release.version) <= version_key(current_version):
            continue
        ignored = ignored_updates.get(game.game_id, {})
        ignored_version = version_key(ignored.get("version"))
        if ignored_version is not None and version_key(release.version) <= ignored_version:
            continue
        notes_baseline = (
            ignored["version"]
            if ignored_version is not None
            and ignored_version > version_key(current_version)
            else current_version
        )
        if release.notes_url not in notes_cache:
            notes_cache[release.notes_url] = fetcher(release.notes_url)
        relevant = release_notes_since(
            notes_cache[release.notes_url],
            notes_baseline,
            release.version,
        )
        if not relevant:
            continue
        updates.append(
            SternUpdate(
                game.game_id,
                game.name,
                current_version,
                release,
                relevant,
                summarize_release_notes(relevant),
                substantial_release_notes(relevant),
            )
        )
    return updates


def _set_release_metadata(path, release):
    data = load_yaml(path)
    basis = data.setdefault("rules_basis", {})
    basis.update(
        {
            "kind": "code",
            "version": release.version,
            "release_date": release.release_date,
        }
    )
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def _record_ignored_update(update, content_directory=CONTENT):
    state_path = _ignored_updates_path(content_directory)
    data = _load_ignored_updates(content_directory)
    data[update.game_id] = {
        "version": update.release.version,
        "release_date": update.release.release_date,
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".stern-code-ignores-",
        dir=state_path.parent,
    ) as directory:
        candidate = Path(directory) / state_path.name
        candidate.write_text(
            yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        candidate.replace(state_path)


def _apply_minor_update(update):
    content_path = CONTENT / f"{update.game_id}.yaml"
    original = content_path.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(
        prefix=f".{update.game_id}-code-",
        dir=CONTENT,
    ) as directory:
        candidate = Path(directory) / content_path.name
        candidate.write_text(original, encoding="utf-8")
        _set_release_metadata(candidate, update.release)
        if not validate_game_contexts(candidate, update.game_id):
            print("Code metadata update was discarded because rendering failed.")
            return 1
        candidate.replace(content_path)
    print(
        f"Updated {content_path.relative_to(ROOT)} to code "
        f"{update.release.version} ({update.release.release_date})."
    )
    description = _update_description(update.game_id)
    return _validate_and_offer_update_packets(update.game_id, description, True)


def _apply_substantial_update(update):
    description = (
        f"{_update_description(update.game_id)}. Re-research for Stern code "
        f"{update.release.version}, released {update.release.release_date}. "
        f"Official release notes: {update.release.notes_url}"
    )
    if not _refresh_content_with_review(
        update.game_id,
        description,
        candidate_transform=lambda path: _set_release_metadata(path, update.release),
        allow_stale_shot_labels=True,
    ):
        return 1
    content_path = CONTENT / f"{update.game_id}.yaml"
    if shot_label_issue(load_yaml(content_path)):
        print("The researched shot list changed; redo its playfield labels now.")
        if interactive_shot_labels(update.game_id, continue_batch=False):
            return 1
    return _validate_and_offer_update_packets(update.game_id, description, True)


def check_stern_code_updates(fetcher=fetch_text, content_directory=CONTENT):
    print(f"Checking Stern game-code releases at {STERN_CODE_URL}...")
    try:
        page = fetcher(STERN_CODE_URL)
        updates = discover_stern_updates(page, fetcher, content_directory)
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"ERROR: could not check Stern code updates: {error}", file=sys.stderr)
        return 1
    if not updates:
        print("No newer Stern code releases matched the local catalog.")
        return 0

    print(f"Found {len(updates)} Stern code update(s).")
    for update in updates:
        print(
            f"\n{update.game_name} [{update.game_id}]: "
            f"{update.current_version} -> {update.release.version} "
            f"({update.release.release_date})"
        )
        for item in update.summary:
            print(f"  - {item}")
        if update.substantial:
            print("Substantial rules/content changes detected; starting full re-research.")
            result = _apply_substantial_update(update)
        elif ask_yes_no("Apply this short code update and update affected binders?"):
            result = _apply_minor_update(update)
        else:
            try:
                _record_ignored_update(update, content_directory)
            except (OSError, yaml.YAMLError) as error:
                print(
                    f"ERROR: could not record skipped code update: {error}",
                    file=sys.stderr,
                )
                return 1
            print(
                f"Skipped through code {update.release.version}; "
                "future checks will not ask about it again."
            )
            result = 0
        if result:
            return result
    return 0
