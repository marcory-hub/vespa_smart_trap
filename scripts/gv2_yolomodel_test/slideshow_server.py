#!/usr/bin/env python3
"""
GV2 YOLO image slideshow server (local-only).

The benchmark runner posts JSON to `POST /show`:
  - image_path: absolute or relative path (optional, used for filename derivation)
  - filename: basename of the image (used as the lookup key)

The server serves:
  - `GET /` a minimal HTML page showing the current image
  - `GET /current` JSON describing the currently selected filename
  - `GET /static/<filename>` the image bytes from the configured images root
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import unquote


_STATE_LOCK = threading.Lock()
_CURRENT_FILENAME: Optional[str] = None


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _read_json_body(handler: BaseHTTPRequestHandler) -> dict:
    content_length_raw = handler.headers.get("Content-Length", "0")
    try:
        content_length = int(content_length_raw)
    except ValueError:
        content_length = 0

    if content_length <= 0:
        return {}

    raw = handler.rfile.read(content_length)
    if not raw:
        return {}

    return json.loads(raw.decode("utf-8", errors="strict"))


def _safe_basename(name: str) -> str:
    # Prevent path traversal: keep only the final path segment.
    return Path(name).name


class SlideshowRequestHandler(BaseHTTPRequestHandler):
    server_version = "GV2Slideshow/1.0"

    def do_GET(self) -> None:  # noqa: N802 (BaseHTTPRequestHandler uses camelCase)
        if self.path.startswith("/current"):
            with _STATE_LOCK:
                filename = _CURRENT_FILENAME
            _json_response(
                self,
                HTTPStatus.OK,
                {
                    "filename": filename,
                    "image_url": f"/static/{filename}" if filename else None,
                },
            )
            return

        if self.path == "/":
            self._serve_index_html()
            return

        if self.path.startswith("/static/"):
            self._serve_static_image()
            return

        _json_response(self, HTTPStatus.NOT_FOUND, {"error": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        if not self.path.startswith("/show"):
            _json_response(self, HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return

        try:
            payload = _read_json_body(self)
        except Exception as e:
            _json_response(self, HTTPStatus.BAD_REQUEST, {"error": f"Invalid JSON: {e}"})
            return

        filename_from_payload = None
        if isinstance(payload.get("filename"), str):
            filename_from_payload = payload["filename"]

        image_path_from_payload = None
        if isinstance(payload.get("image_path"), str):
            image_path_from_payload = payload["image_path"]

        if filename_from_payload:
            filename = _safe_basename(filename_from_payload)
        elif image_path_from_payload:
            filename = _safe_basename(image_path_from_payload)
        else:
            _json_response(self, HTTPStatus.BAD_REQUEST, {"error": "Missing filename or image_path"})
            return

        images_root: Path = self.server.images_root  # type: ignore[attr-defined]
        requested_path = images_root / filename
        if not requested_path.exists():
            _json_response(
                self,
                HTTPStatus.NOT_FOUND,
                {"error": f"Image not found in images_root: {filename}"},
            )
            return

        with _STATE_LOCK:
            global _CURRENT_FILENAME
            _CURRENT_FILENAME = filename

        _json_response(self, HTTPStatus.OK, {"ok": True, "filename": filename})

    def _serve_index_html(self) -> None:
        # target ~10 cm wide at approx 378px on the tester's setup (see plan)
        html = """<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>GV2 Slideshow</title>
  <style>
    :root {
      --bg: #0b1020;
      --fg: #e7eefc;
      --muted: #98a3c7;
      --accent: #66e3ff;
      --panel: rgba(255,255,255,0.06);
      --panel2: rgba(255,255,255,0.10);
    }
    body {
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      background:
        radial-gradient(1200px 600px at 20% -10%, rgba(102,227,255,0.22), transparent 60%),
        radial-gradient(900px 500px at 90% 10%, rgba(120,92,255,0.20), transparent 55%),
        var(--bg);
      color: var(--fg);
    }
    .wrap {
      padding: 20px 24px 40px;
      max-width: 980px;
    }
    h1 {
      font-size: 18px;
      letter-spacing: 0.2px;
      margin: 6px 0 12px;
      font-weight: 600;
    }
    #cal-note {
      background: var(--panel);
      border: 1px solid var(--panel2);
      border-radius: 14px;
      padding: 12px 14px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.35;
      margin-bottom: 14px;
    }
    #img {
      width: 378px; /* plan estimate */
      max-width: 100%;
      height: auto;
      border-radius: 12px;
      border: 1px solid rgba(231,238,252,0.18);
      background: rgba(0,0,0,0.25);
      box-shadow: 0 12px 28px rgba(0,0,0,0.35);
      display: block;
    }
    #status {
      margin-top: 12px;
      color: var(--muted);
      font-size: 13px;
      white-space: pre-wrap;
    }
    .dot {
      display: inline-block;
      width: 8px;
      height: 8px;
      border-radius: 99px;
      background: var(--accent);
      margin-right: 8px;
      box-shadow: 0 0 0 6px rgba(102,227,255,0.12);
      transform: translateY(1px);
    }
    code { color: var(--fg); }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>GV2 Image Slideshow</h1>
    <div id="cal-note">
      Display calibration: show images at approximately 10 cm wide (~378px).
      <strong>[to be verified by user]</strong>
    </div>
    <img id="img" alt="current image" src="" />
    <div id="status"><span class="dot"></span>Waiting for <code>/show</code>...</div>
  </div>
  <script>
    async function refresh() {
      try {
        const res = await fetch('/current?ts=' + Date.now());
        const data = await res.json();
        const img = document.getElementById('img');
        const status = document.getElementById('status');
        if (data.filename) {
          img.src = '/static/' + encodeURIComponent(data.filename) + '?v=' + Date.now();
          status.textContent = 'Current: ' + data.filename;
        } else {
          status.textContent = 'Waiting for first image...';
          img.removeAttribute('src');
        }
      } catch (e) {
        // Keep polling even if a request fails temporarily.
      }
    }
    setInterval(refresh, 250);
    refresh();
  </script>
</body>
</html>
"""
        body = html.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_static_image(self) -> None:
        images_root: Path = self.server.images_root  # type: ignore[attr-defined]

        # e.g. /static/filename.jpg
        parts = self.path.split("/", 2)
        if len(parts) < 3:
            _json_response(self, HTTPStatus.BAD_REQUEST, {"error": "Invalid /static path"})
            return

        requested_name = unquote(parts[2].split("?", 1)[0])
        filename = _safe_basename(requested_name)
        image_path = images_root / filename
        if not image_path.exists():
            _json_response(self, HTTPStatus.NOT_FOUND, {"error": "Image not found"})
            return

        mime_type, _ = mimetypes.guess_type(str(image_path))
        if not mime_type:
            mime_type = "application/octet-stream"

        data = image_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mime_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args) -> None:  # noqa: A002 (BaseHTTPRequestHandler API)
        # Keep console output minimal so benchmark logs stay readable.
        return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local slideshow server for GV2 benchmarking.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host.")
    parser.add_argument("--port", type=int, default=8000, help="Bind port.")

    # Default should match benchmark_runner.py's default images_dir: data/test/images.
    default_images_root = Path(__file__).resolve().parents[2] / "data/test/images"
    parser.add_argument("--images-root", default=str(default_images_root), help="Root containing test images.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    images_root = Path(args.images_root).expanduser().resolve()
    if not images_root.exists():
        raise SystemExit(f"ERROR: images-root does not exist: {images_root}")

    # Plan alignment: show one image immediately on `/` if possible.
    # This avoids a blank page until the first POST /show.
    default_images = sorted(images_root.glob("*.jpg"))
    if default_images:
        default_filename = default_images[0].name
        with _STATE_LOCK:
            global _CURRENT_FILENAME
            _CURRENT_FILENAME = default_filename

    server = ThreadingHTTPServer((args.host, args.port), SlideshowRequestHandler)
    # Attach to handler via `self.server.images_root`.
    server.images_root = images_root  # type: ignore[attr-defined]

    print(f"Slideshow server listening on http://{args.host}:{args.port}")
    print(f"Images root: {images_root}")
    server.serve_forever()


if __name__ == "__main__":
    main()

