from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import mimetypes
import os
import posixpath
import random
import re
import sys
import urllib.parse
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Optional


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = Path(__file__).resolve().parent / "static"
IMAGES_DIR = WORKSPACE_ROOT / "data" / "test" / "images"
OUTPUTS_DIR = Path(__file__).resolve().parent / "outputs"

INTRO_TEXT = "Resize the browser image to 10 cm (use the bar), then place the camera 10 cm from the screen."

VIEWPOINT_TOKENS = {"oth", "sid", "top"}
SPECIES_TOKENS = {"ame", "vcr", "ves", "vve", "NUL"}

FILENAME_PREFIX_RE = re.compile(r"^(?P<viewpoint>[a-z]{3})_(?P<species>[A-Za-z]{3})")


def _iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def _safe_join(base_dir: Path, *parts: str) -> Optional[Path]:
    candidate = base_dir
    for part in parts:
        if part in {"", ".", ".."}:
            return None
        candidate = candidate / part
    try:
        resolved = candidate.resolve()
    except FileNotFoundError:
        resolved = candidate.absolute()
    if base_dir.resolve() not in resolved.parents and resolved != base_dir.resolve():
        return None
    return resolved


def _list_images() -> list[Path]:
    return sorted(IMAGES_DIR.glob("*.jpg"))


def _parse_tokens_from_basename(basename: str) -> tuple[str, str]:
    match = FILENAME_PREFIX_RE.match(basename)
    if not match:
        raise ValueError("missing vvv_sss prefix")
    viewpoint = match.group("viewpoint")
    species = match.group("species")
    if viewpoint not in VIEWPOINT_TOKENS:
        raise ValueError(f"invalid viewpoint token: {viewpoint!r}")
    if species not in SPECIES_TOKENS:
        raise ValueError(f"invalid species token: {species!r}")
    return viewpoint, species


def _seeded_shuffle(items: list[str], seed: int) -> list[str]:
    rng = random.Random(seed)
    shuffled = list(items)
    rng.shuffle(shuffled)
    return shuffled


@dataclass(frozen=True)
class ManifestItem:
    index: int
    filename: str
    url: str
    viewpoint: str
    species: str


@dataclass
class CurrentRun:
    run_id: str
    run_dir: Path
    log_path: Path


class SliderServerState:
    def __init__(self) -> None:
        self._current_run: Optional[CurrentRun] = None

    def start_new_run(self) -> CurrentRun:
        timestamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        run_dir = OUTPUTS_DIR / timestamp
        run_dir.mkdir(parents=True, exist_ok=False)
        log_path = run_dir / "run_log.csv"
        with log_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["index", "filename", "viewpoint", "species", "shown_at_iso"])
        run = CurrentRun(run_id=timestamp, run_dir=run_dir, log_path=log_path)
        self._current_run = run
        return run

    def current_run(self) -> Optional[CurrentRun]:
        return self._current_run


STATE = SliderServerState()


class SliderRequestHandler(BaseHTTPRequestHandler):
    server_version = "ImageSliderWeb/1.0"

    def _send_json(self, status: int, payload: Any) -> None:
        data = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_text(self, status: int, text: str, content_type: str = "text/plain; charset=utf-8") -> None:
        data = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json_body(self) -> Any:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b""
        if not raw:
            return None
        return json.loads(raw.decode("utf-8"))

    def log_message(self, fmt: str, *args: Any) -> None:
        # Keep terminal output compact; still show errors via responses.
        return

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/":
            return self._serve_static_file("index.html")
        if path == "/app.js":
            return self._serve_static_file("app.js")
        if path == "/style.css":
            return self._serve_static_file("style.css")

        if path in {"/api/manifest", "/manifest.json"}:
            return self._handle_manifest()
        if path == "/start":
            return self._handle_start()

        if path.startswith("/images/"):
            filename = path[len("/images/") :]
            return self._serve_image_file(filename)

        self._send_text(HTTPStatus.NOT_FOUND, "Not found\n")

    def do_POST(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path == "/log":
            return self._handle_log()
        self._send_text(HTTPStatus.NOT_FOUND, "Not found\n")

    def _serve_static_file(self, name: str) -> None:
        file_path = _safe_join(STATIC_DIR, name)
        if not file_path or not file_path.exists() or not file_path.is_file():
            self._send_text(HTTPStatus.NOT_FOUND, "Not found\n")
            return
        content = file_path.read_bytes()
        guessed_type, _ = mimetypes.guess_type(str(file_path))
        content_type = guessed_type or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _serve_image_file(self, filename: str) -> None:
        filename = posixpath.basename(filename)
        if not filename.lower().endswith(".jpg"):
            self._send_text(HTTPStatus.BAD_REQUEST, "Only .jpg is allowed\n")
            return
        file_path = _safe_join(IMAGES_DIR, filename)
        if not file_path or not file_path.exists() or not file_path.is_file():
            self._send_text(HTTPStatus.NOT_FOUND, "Image not found\n")
            return
        content = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _handle_start(self) -> None:
        try:
            run = STATE.start_new_run()
        except FileExistsError:
            self._send_text(HTTPStatus.CONFLICT, "Run folder already exists; retry\n")
            return
        self._send_json(
            HTTPStatus.OK,
            {
                "run_id": run.run_id,
                "log_path": str(run.log_path.relative_to(WORKSPACE_ROOT)),
                "intro_text": INTRO_TEXT,
            },
        )

    def _handle_manifest(self) -> None:
        if not IMAGES_DIR.exists():
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": "images directory does not exist", "path": str(IMAGES_DIR)},
            )
            return

        images = _list_images()
        basenames = [p.name for p in images]

        errors: list[dict[str, str]] = []
        parsed: list[tuple[str, str, str]] = []
        for name in basenames:
            try:
                viewpoint, species = _parse_tokens_from_basename(Path(name).stem)
                parsed.append((name, viewpoint, species))
            except ValueError as e:
                errors.append({"filename": name, "reason": str(e)})

        if errors:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {
                    "error": "invalid filenames (fail fast)",
                    "expected": {
                        "prefix_format": "vvv_sss (first 7 characters of basename)",
                        "viewpoint_tokens": sorted(VIEWPOINT_TOKENS),
                        "species_tokens": sorted(SPECIES_TOKENS),
                    },
                    "bad_files": errors,
                },
            )
            return

        sorted_names = sorted([t[0] for t in parsed])
        shuffled_names = _seeded_shuffle(sorted_names, seed=42)

        token_map = {name: (viewpoint, species) for (name, viewpoint, species) in parsed}
        items: list[ManifestItem] = []
        for idx, filename in enumerate(shuffled_names, start=1):
            viewpoint, species = token_map[filename]
            items.append(
                ManifestItem(
                    index=idx,
                    filename=filename,
                    url=f"/images/{urllib.parse.quote(filename)}",
                    viewpoint=viewpoint,
                    species=species,
                )
            )

        self._send_json(
            HTTPStatus.OK,
            {
                "count": len(items),
                "seed": 42,
                "items": [item.__dict__ for item in items],
            },
        )

    def _handle_log(self) -> None:
        run = STATE.current_run()
        if not run:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "run not started; call /start first"})
            return

        try:
            payload = self._read_json_body()
        except json.JSONDecodeError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid json"})
            return

        if not isinstance(payload, dict):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "expected json object"})
            return

        required = {"index", "filename", "viewpoint", "species", "shown_at_iso"}
        missing = sorted(required - set(payload.keys()))
        if missing:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "missing fields", "missing": missing})
            return

        row = [
            str(payload["index"]),
            str(payload["filename"]),
            str(payload["viewpoint"]),
            str(payload["species"]),
            str(payload["shown_at_iso"]),
        ]
        with run.log_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)

        self._send_json(HTTPStatus.OK, {"ok": True})


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Local image slider web server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv[1:])

    host = args.host
    port = args.port

    if not STATIC_DIR.exists():
        print(f"Static directory missing: {STATIC_DIR}", file=sys.stderr)
        return 2
    if not OUTPUTS_DIR.exists():
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    httpd = ThreadingHTTPServer((host, port), SliderRequestHandler)
    print(f"Serving on http://{host}:{port}")
    print(f"Images dir: {IMAGES_DIR}")
    return_code = 0
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return return_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
