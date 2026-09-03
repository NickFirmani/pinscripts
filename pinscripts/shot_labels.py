"""Interactive placement and rendering of numbered playfield shot labels."""

from __future__ import annotations

import hashlib
import io
import json
import secrets
import sys
import tempfile
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import yaml
from PIL import Image, ImageDraw, ImageFont, ImageOps, UnidentifiedImageError

from .content import PinRegistryError, content_for_selected_pins, load_yaml
from .paths import CONTENT, ROOT, SHOT_LABELS


LABEL_VERSION = 1
MARKER_RADIUS_RATIO = 0.042
MARKER_FILL = "#176B75"
MARKER_FILL_BW = "#142735"
MARKER_EDGE = "#142735"
MARKER_RING = "#FFFFFF"
MARKER_TEXT = "#FFFFFF"


class ShotLabelError(ValueError):
    """Raised when shot-label metadata is missing, stale, or malformed."""


def oriented_image(path: Path):
    """Open an image and normalize its EXIF orientation before using coordinates."""
    with Image.open(path) as source:
        return ImageOps.exif_transpose(source).copy()


def image_fingerprint(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def marker_radius(image_size):
    return max(12, round(min(image_size) * MARKER_RADIUS_RATIO))


def _marker_font(radius):
    try:
        return ImageFont.load_default(size=max(12, round(radius * 1.15)))
    except TypeError:  # Pillow 10.0 did not yet accept a scalable default size.
        return ImageFont.load_default()


def draw_shot_labels(image, coordinates, black_and_white=False):
    """Return a copy of ``image`` with the configured shot markers painted on it."""
    annotated = image.convert("RGB")
    draw = ImageDraw.Draw(annotated)
    radius = marker_radius(annotated.size)
    ring_inset = max(2, round(radius * 0.08))
    fill_inset = max(ring_inset + 2, round(radius * 0.18))
    fill = MARKER_FILL_BW if black_and_white else MARKER_FILL
    font = _marker_font(radius)

    for point in coordinates:
        x = int(point["x"])
        y = int(point["y"])
        diagram = str(point["diagram"])
        box = (x - radius, y - radius, x + radius, y + radius)
        draw.ellipse(box, fill=MARKER_EDGE)
        draw.ellipse(
            tuple(
                value + ring_inset if index < 2 else value - ring_inset
                for index, value in enumerate(box)
            ),
            fill=MARKER_RING,
        )
        draw.ellipse(
            tuple(
                value + fill_inset if index < 2 else value - fill_inset
                for index, value in enumerate(box)
            ),
            fill=fill,
        )
        text_box = draw.textbbox((0, 0), diagram, font=font, stroke_width=1)
        text_width = text_box[2] - text_box[0]
        text_height = text_box[3] - text_box[1]
        draw.text(
            (x - text_width / 2, y - text_height / 2 - text_box[1]),
            diagram,
            font=font,
            fill=MARKER_TEXT,
            stroke_width=1,
            stroke_fill=MARKER_TEXT,
        )
    return annotated


def label_path_for_game(game_id, labels_directory=None):
    labels_directory = labels_directory or SHOT_LABELS
    return labels_directory / f"{game_id}.yaml"


def labels_directory_for_root(root):
    return root / "content" / "shot-labels"


def _expected_diagrams(data):
    diagrams = [shot.get("diagram") for shot in data.get("shots", [])]
    if len(set(diagrams)) != len(diagrams):
        raise ShotLabelError("shot diagram numbers must be unique")
    return diagrams


def shot_fingerprint(data):
    identity = [
        {"diagram": shot.get("diagram"), "name": shot.get("name")}
        for shot in data.get("shots", [])
    ]
    encoded = json.dumps(identity, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _validate_label_document(document, data, image_path):
    if not isinstance(document, dict):
        raise ShotLabelError("shot-label file must contain a mapping")

    required = {
        "version",
        "game_id",
        "image",
        "image_width",
        "image_height",
        "image_sha256",
        "shots_sha256",
        "coordinates",
    }
    if set(document) != required:
        missing = sorted(required - set(document))
        extra = sorted(set(document) - required)
        details = []
        if missing:
            details.append("missing " + ", ".join(missing))
        if extra:
            details.append("unknown " + ", ".join(extra))
        raise ShotLabelError("invalid shot-label fields: " + "; ".join(details))

    if document["version"] != LABEL_VERSION:
        raise ShotLabelError(
            f"unsupported shot-label version {document['version']!r}"
        )
    if document["game_id"] != data.get("id"):
        raise ShotLabelError("shot labels belong to a different game")
    if document["image"] != data.get("image"):
        raise ShotLabelError("the configured image changed; redo shot labels")

    try:
        with oriented_image(image_path) as image:
            current_size = image.size
    except (OSError, UnidentifiedImageError) as error:
        raise ShotLabelError(f"could not inspect image: {error}") from error

    recorded_size = (document["image_width"], document["image_height"])
    if recorded_size != current_size:
        raise ShotLabelError(
            "image dimensions changed from "
            f"{recorded_size[0]}x{recorded_size[1]} to "
            f"{current_size[0]}x{current_size[1]}; redo shot labels"
        )
    if document["image_sha256"] != image_fingerprint(image_path):
        raise ShotLabelError("image contents changed; redo shot labels")
    if document["shots_sha256"] != shot_fingerprint(data):
        raise ShotLabelError("shot list or diagram numbering changed; redo shot labels")

    coordinates = document["coordinates"]
    if not isinstance(coordinates, list):
        raise ShotLabelError("coordinates must be a list")
    expected = _expected_diagrams(data)
    diagram_groups = []
    for index, point in enumerate(coordinates):
        if not isinstance(point, dict) or set(point) != {"diagram", "x", "y"}:
            raise ShotLabelError(f"coordinate {index + 1} is malformed")
        diagram, x, y = point["diagram"], point["x"], point["y"]
        if not all(
            isinstance(value, int) and not isinstance(value, bool)
            for value in (diagram, x, y)
        ):
            raise ShotLabelError(f"coordinate {index + 1} must use integers")
        if not 0 <= x < current_size[0] or not 0 <= y < current_size[1]:
            raise ShotLabelError(
                f"coordinate for diagram {diagram} is outside the image"
            )
        if not diagram_groups or diagram_groups[-1] != diagram:
            if diagram in diagram_groups:
                raise ShotLabelError(
                    "labels for the same shot must be stored together"
                )
            diagram_groups.append(diagram)
    if diagram_groups != expected:
        raise ShotLabelError(
            "shot list or diagram numbering changed; redo shot labels"
        )
    return document


def load_shot_labels(data, root=ROOT, labels_directory=None):
    """Load current labels, returning ``None`` when a game has not been labeled."""
    path = label_path_for_game(
        data.get("id"),
        labels_directory or labels_directory_for_root(root),
    )
    if not path.is_file():
        return None
    try:
        document = load_yaml(path)
    except (OSError, yaml.YAMLError) as error:
        raise ShotLabelError(f"could not read {path}: {error}") from error
    image_path = root / data.get("image", "")
    return _validate_label_document(document, data, image_path)


def write_shot_labels(data, image_path, coordinates, labels_directory=None):
    labels_directory = labels_directory or SHOT_LABELS
    labels_directory.mkdir(parents=True, exist_ok=True)
    with oriented_image(image_path) as image:
        width, height = image.size
    document = {
        "version": LABEL_VERSION,
        "game_id": data["id"],
        "image": data["image"],
        "image_width": width,
        "image_height": height,
        "image_sha256": image_fingerprint(image_path),
        "shots_sha256": shot_fingerprint(data),
        "coordinates": coordinates,
    }
    _validate_label_document(document, data, image_path)
    destination = label_path_for_game(data["id"], labels_directory)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix=f".{data['id']}-",
        suffix=".yaml",
        dir=labels_directory,
        delete=False,
    ) as temporary:
        yaml.safe_dump(document, temporary, sort_keys=False, allow_unicode=True)
        temporary_path = Path(temporary.name)
    temporary_path.replace(destination)
    return destination


def shot_label_issue(data, root=ROOT, labels_directory=None):
    path = label_path_for_game(
        data.get("id"),
        labels_directory or labels_directory_for_root(root),
    )
    if not path.is_file():
        return "shot coordinates are missing"
    try:
        load_shot_labels(data, root, labels_directory)
    except ShotLabelError as error:
        return str(error)
    return None


def first_game_needing_labels(paths=None, root=ROOT, labels_directory=None):
    paths = paths if paths is not None else content_for_selected_pins()
    for path in paths:
        data = load_yaml(path)
        image = data.get("image")
        if not image or not (root / image).is_file():
            continue
        issue = shot_label_issue(data, root, labels_directory)
        if issue:
            return path, issue
    return None, None


class _LabelSession:
    def __init__(
        self,
        data,
        image_path,
        labels_directory,
        next_game_loader=None,
    ):
        self.labels_directory = labels_directory
        self.next_game_loader = next_game_loader
        self.saved_paths = []
        self.finished = threading.Event()
        self.lock = threading.Lock()
        self.batch_complete = False
        self.message = ""
        self.revision = 0
        self._load_game(data, image_path)

    def _load_game(self, data, image_path):
        self.data = data
        self.image_path = image_path
        with oriented_image(image_path) as image:
            self.width, self.height = image.size
        self.shots = data["shots"]
        self.coordinates = []
        self.current_index = 0
        self.extra_for_index = None
        self.revision += 1

    def _shot_details(self, index):
        if index is None or not 0 <= index < len(self.shots):
            return None
        shot = self.shots[index]
        return {
            "diagram": shot["diagram"],
            "name": shot["name"],
            "description": shot.get("value", ""),
            "difficulty": shot.get("risk", ""),
        }

    def state(self):
        with self.lock:
            complete = self.current_index == len(self.shots)
            active_index = (
                self.extra_for_index
                if self.extra_for_index is not None
                else self.current_index if not complete else None
            )
            previous_index = self.current_index - 1
            return {
                "game": self.data["name"],
                "width": self.width,
                "height": self.height,
                "active_shot": self._shot_details(active_index),
                "previous_shot": self._shot_details(previous_index),
                "coordinates": list(self.coordinates),
                "shots_placed": self.current_index,
                "shot_count": len(self.shots),
                "label_count": len(self.coordinates),
                "placing_extra": self.extra_for_index is not None,
                "complete": complete,
                "batch_complete": self.batch_complete,
                "message": self.message,
                "revision": self.revision,
            }

    def place(self, x, y):
        with self.lock:
            if self.batch_complete:
                return
            if self.extra_for_index is not None:
                shot_index = self.extra_for_index
                self.extra_for_index = None
            elif self.current_index < len(self.shots):
                shot_index = self.current_index
                self.current_index += 1
            else:
                return
            shot = self.shots[shot_index]
            self.coordinates.append(
                {
                    "diagram": shot["diagram"],
                    "x": max(0, min(self.width - 1, round(float(x)))),
                    "y": max(0, min(self.height - 1, round(float(y)))),
                }
            )
            self.revision += 1
            self.message = ""

    def add_another(self):
        with self.lock:
            if (
                self.batch_complete
                or self.extra_for_index is not None
                or self.current_index == 0
            ):
                return
            self.extra_for_index = self.current_index - 1
            self.revision += 1
            self.message = ""

    def back(self):
        with self.lock:
            if self.extra_for_index is not None:
                self.extra_for_index = None
                self.revision += 1
                return
            if self.coordinates:
                point = self.coordinates.pop()
                diagram = point["diagram"]
                if not any(item["diagram"] == diagram for item in self.coordinates):
                    shot_index = next(
                        index
                        for index, shot in enumerate(self.shots)
                        if shot["diagram"] == diagram
                    )
                    self.current_index = min(self.current_index, shot_index)
                self.revision += 1
                self.message = ""

    def reset(self):
        with self.lock:
            self.coordinates.clear()
            self.current_index = 0
            self.extra_for_index = None
            self.revision += 1
            self.message = ""

    def save(self):
        with self.lock:
            if (
                self.current_index != len(self.shots)
                or self.extra_for_index is not None
            ):
                raise ShotLabelError("place every shot before saving")
            coordinates = list(self.coordinates)
            saved_game = self.data["name"]
            data = self.data
            image_path = self.image_path
        destination = write_shot_labels(
            data,
            image_path,
            coordinates,
            self.labels_directory,
        )
        self.saved_paths.append(destination)

        try:
            next_game = self.next_game_loader() if self.next_game_loader else None
        except (
            KeyError,
            OSError,
            PinRegistryError,
            ShotLabelError,
            UnidentifiedImageError,
            yaml.YAMLError,
        ) as error:
            with self.lock:
                self.batch_complete = True
                self.message = (
                    f"Saved {saved_game}, but could not load the next game: "
                    f"{error}"
                )
                self.revision += 1
            self.finished.set()
            return
        if next_game is None:
            with self.lock:
                self.batch_complete = True
                self.message = f"Saved {saved_game}. Every selected game is labeled."
                self.revision += 1
            self.finished.set()
            return

        data, image_path, issue = next_game
        with self.lock:
            self._load_game(data, image_path)
            self.message = f"Saved {saved_game}. Loaded the next game: {issue}."

    def cancel(self):
        self.finished.set()

    def preview(self):
        with self.lock:
            coordinates = list(self.coordinates)
            image_path = self.image_path
        with oriented_image(image_path) as image:
            annotated = draw_shot_labels(image, coordinates)
        output = io.BytesIO()
        annotated.save(output, "PNG")
        return output.getvalue()


def _page_html(token):
    base = f"/{token}"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Place shot labels</title>
<style>
:root {{ color-scheme: dark; font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: #091722; color: #eef5f6; min-height: 100vh; }}
main {{ display: grid; grid-template-columns: minmax(0,1fr) 360px; gap: 20px; padding: 20px; min-height: 100vh; }}
.stage {{ display:flex; align-items:center; justify-content:center; min-width:0; }}
#board {{ display:block; max-width:100%; max-height:calc(100vh - 40px); width:auto; height:auto; cursor:crosshair; border:1px solid #52636d; box-shadow:0 14px 45px #0009; }}
aside {{ align-self:center; background:#142735; border:1px solid #53636c; border-radius:14px; padding:20px; box-shadow:0 14px 45px #0007; }}
.eyebrow {{ color:#73cbd1; font-size:12px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; }}
h1 {{ font-size:23px; margin:6px 0 4px; }}
#progress {{ color:#aab8bd; font-size:13px; }}
#notice {{ color:#73cbd1; font-size:13px; line-height:1.4; margin-top:12px; }}
#instruction {{ margin:20px 0 12px; font-size:17px; font-weight:700; line-height:1.4; }}
#details {{ background:#0d202d; border:1px solid #405865; border-radius:9px; padding:13px; margin-bottom:16px; }}
#shot-name {{ font-weight:750; margin-bottom:7px; }} #description {{ color:#cfdbdf; font-size:14px; line-height:1.45; }}
#difficulty {{ display:inline-block; background:#254858; border-radius:999px; color:#fff; font-size:12px; font-weight:700; margin-top:10px; padding:4px 9px; }}
button {{ appearance:none; border:1px solid #71828a; border-radius:8px; background:#203b4b; color:#fff; font:inherit; font-weight:650; padding:10px 13px; cursor:pointer; }}
button:hover:not(:disabled) {{ background:#2b5062; }} button:disabled {{ opacity:.4; cursor:default; }}
#save {{ width:100%; background:#176b75; border-color:#56aeb5; margin-top:10px; }}
.row {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:8px; }}
#reset {{ width:100%; margin-top:8px; }}
#cancel {{ width:100%; border:0; background:transparent; color:#aab8bd; margin-top:8px; }}
.hint {{ color:#8fa0a8; font-size:12px; line-height:1.45; margin-top:18px; }}
@media (max-width:800px) {{ main {{ grid-template-columns:1fr; }} #board {{ max-height:70vh; }} aside {{ width:min(100%,560px); justify-self:center; }} }}
</style></head><body><main><div class="stage"><img id="board" alt="Playfield"></div>
<aside><div class="eyebrow">Shot label editor</div><h1 id="game">Loading…</h1><div id="progress"></div>
<div id="notice"></div><div id="instruction"></div>
<div id="details"><div id="shot-name"></div><div id="description"></div><div id="difficulty"></div></div>
<div class="row"><button id="another">Add another</button><button id="back">Back</button></div><button id="reset">Start over</button>
<button id="save">Save &amp; next game</button><button id="cancel">Stop without saving this game</button>
<div class="hint">Each click advances to the next shot. Use Add another when one table entry has multiple physical targets. Back removes the most recent marker. Saving automatically loads the next unlabeled game.</div></aside>
</main><script>
const base={json.dumps(base)}; let state=null;
async function request(action, body={{}}) {{
  const response=await fetch(`${{base}}/${{action}}`,{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(body)}});
  if(!response.ok) throw new Error(await response.text());
  state=await response.json(); render();
}}
async function load() {{ state=await (await fetch(`${{base}}/state`)).json(); render(); }}
function render() {{
  document.querySelector('#game').textContent=state.game;
  document.querySelector('#progress').textContent=`${{state.shots_placed}} of ${{state.shot_count}} shots · ${{state.label_count}} labels`;
  document.querySelector('#notice').textContent=state.message;
  const instruction=document.querySelector('#instruction');
  if(state.batch_complete) instruction.textContent='All selected games are labeled.';
  else if(state.placing_extra) instruction.textContent=`Click another location for shot ${{state.active_shot.diagram}}.`;
  else if(state.complete) instruction.textContent='Review the image, then save or go back.';
  else instruction.textContent=`Click shot ${{state.active_shot.diagram}}.`;
  const details=document.querySelector('#details'); const shot=state.active_shot;
  details.hidden=!shot;
  if(shot) {{
    document.querySelector('#shot-name').textContent=shot.name;
    document.querySelector('#description').textContent=shot.description;
    const difficulty=document.querySelector('#difficulty');
    difficulty.textContent=shot.difficulty ? `Difficulty: ${{shot.difficulty}}` : 'Difficulty: not specified';
  }}
  const another=document.querySelector('#another');
  another.disabled=state.batch_complete || state.placing_extra || !state.previous_shot;
  another.textContent=state.previous_shot ? `Another #${{state.previous_shot.diagram}}` : 'Add another';
  document.querySelector('#back').disabled=state.label_count===0 && !state.placing_extra;
  document.querySelector('#reset').disabled=state.label_count===0;
  document.querySelector('#save').disabled=state.batch_complete || !state.complete || state.placing_extra;
  document.querySelector('#board').src=`${{base}}/preview.png?v=${{state.revision}}`;
}}
document.querySelector('#board').addEventListener('click', event => {{
  if(!state || state.batch_complete || (state.complete && !state.placing_extra)) return;
  const rect=event.currentTarget.getBoundingClientRect();
  request('place',{{x:(event.clientX-rect.left)*state.width/rect.width,y:(event.clientY-rect.top)*state.height/rect.height}});
}});
document.querySelector('#another').onclick=()=>request('add-another'); document.querySelector('#back').onclick=()=>request('back'); document.querySelector('#reset').onclick=()=>request('reset');
document.querySelector('#save').onclick=()=>request('save'); document.querySelector('#cancel').onclick=()=>request('cancel');
document.addEventListener('keydown',event=>{{ if(event.key==='Backspace'){{event.preventDefault();request('back');}} }}); load();
</script></body></html>"""


def _handler_for(session, token):
    class LabelHandler(BaseHTTPRequestHandler):
        def log_message(self, _format, *_args):
            return

        def _route(self):
            path = urlparse(self.path).path
            prefix = f"/{token}"
            if not path.startswith(prefix):
                return None
            return path[len(prefix):] or "/"

        def _send(self, content, content_type, status=HTTPStatus.OK):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(content)

        def _json(self):
            payload = json.dumps(session.state()).encode("utf-8")
            self._send(payload, "application/json; charset=utf-8")

        def do_GET(self):
            route = self._route()
            if route == "/":
                self._send(
                    _page_html(token).encode("utf-8"),
                    "text/html; charset=utf-8",
                )
            elif route == "/state":
                self._json()
            elif route == "/preview.png":
                self._send(session.preview(), "image/png")
            else:
                self._send(b"Not found", "text/plain", HTTPStatus.NOT_FOUND)

        def do_POST(self):
            route = self._route()
            try:
                length = min(int(self.headers.get("Content-Length", "0")), 4096)
                body = json.loads(self.rfile.read(length) or b"{}")
                if route == "/place":
                    session.place(body["x"], body["y"])
                elif route == "/add-another":
                    session.add_another()
                elif route == "/back":
                    session.back()
                elif route == "/reset":
                    session.reset()
                elif route == "/save":
                    session.save()
                elif route == "/cancel":
                    session.cancel()
                else:
                    self._send(b"Not found", "text/plain", HTTPStatus.NOT_FOUND)
                    return
                self._json()
            except (KeyError, TypeError, ValueError, OverflowError) as error:
                self._send(
                    str(error).encode("utf-8"),
                    "text/plain",
                    HTTPStatus.BAD_REQUEST,
                )

    return LabelHandler


def _content_path_for_game(game):
    supplied = Path(game).expanduser()
    if supplied.is_file():
        return supplied
    return CONTENT / f"{game}.yaml"


def _game_for_editor(content_path, issue="", root=ROOT):
    data = load_yaml(content_path)
    image_path = root / data["image"]
    if not image_path.is_file():
        raise ShotLabelError(f"missing image: {image_path}")
    _expected_diagrams(data)
    return data, image_path, issue


def _remaining_game_loader(current_path, root=ROOT, paths=None):
    paths = list(paths) if paths is not None else content_for_selected_pins()
    resolved_current = current_path.resolve()
    current_index = next(
        (
            index
            for index, path in enumerate(paths)
            if path.resolve() == resolved_current
        ),
        None,
    )
    if current_index is not None:
        paths = paths[current_index + 1:] + paths[:current_index]

    def load_next():
        while paths:
            path = paths.pop(0)
            data = load_yaml(path)
            image = data.get("image")
            if not image or not (root / image).is_file():
                continue
            issue = shot_label_issue(data, root)
            if issue:
                return _game_for_editor(path, issue, root)
        return None

    return load_next


def interactive_shot_labels(game):
    """Open the browser label editor for one game, or the next incomplete game."""
    game = game.strip()
    issue = None
    if game:
        content_path = _content_path_for_game(game)
        if not content_path.is_file():
            print(f"ERROR: no content file: {content_path}", file=sys.stderr)
            return 1
    else:
        try:
            content_path, issue = first_game_needing_labels()
        except (OSError, PinRegistryError, yaml.YAMLError) as error:
            print(f"ERROR: could not select a game: {error}", file=sys.stderr)
            return 1
        if content_path is None:
            print("Every selected game with an available image has current shot labels.")
            return 0

    try:
        data, image_path, _issue = _game_for_editor(content_path, issue or "")
        session = _LabelSession(
            data,
            image_path,
            SHOT_LABELS,
            next_game_loader=_remaining_game_loader(content_path),
        )
        if issue:
            session.message = f"Selected {data['name']}: {issue}."
    except (KeyError, OSError, ShotLabelError, UnidentifiedImageError, yaml.YAMLError) as error:
        print(f"ERROR: could not start shot labeling: {error}", file=sys.stderr)
        return 1

    if issue:
        print(f"Selected {data['id']}: {issue}.")
    elif label_path_for_game(data["id"]).exists():
        print("Existing labels will remain unchanged unless you complete and save this pass.")

    token = secrets.token_urlsafe(18)
    server = ThreadingHTTPServer(("127.0.0.1", 0), _handler_for(session, token))
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/{token}/"
    print(f"Opening shot label editor for {data['name']}: {url}")
    webbrowser.open(url)
    try:
        session.finished.wait()
    except KeyboardInterrupt:
        session.cancel()
        print("\nShot labeling cancelled.")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    if session.saved_paths:
        print(f"Saved shot labels for {len(session.saved_paths)} game(s):")
        for path in session.saved_paths:
            print(f"  {path}")
    else:
        print("Shot labels were not changed.")
    return 0
