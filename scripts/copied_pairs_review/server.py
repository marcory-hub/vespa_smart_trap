#!/usr/bin/env python3
"""Review copied missing pairs. Default: remove all. Keep only top-down samples."""

from __future__ import annotations

import argparse
import csv
import json
import mimetypes
import re
import webbrowser
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, unquote, urlparse

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = Path(__file__).resolve().parent / "static"
DEFAULT_MANIFEST = WORKSPACE_ROOT / "data/copied_missing_pairs/manifest.csv"
DEFAULT_KEPT = WORKSPACE_ROOT / "data/copied_missing_pairs/keep_topdown.json"
LEGACY_REJECTED = WORKSPACE_ROOT / "data/copied_missing_pairs/reject_non_topdown.json"
DEFAULT_REMOVAL_LIST = WORKSPACE_ROOT / "data/copied_missing_pairs/remove_non_topdown.txt"
DEFAULT_KEEP_LIST = WORKSPACE_ROOT / "data/copied_missing_pairs/keep_topdown.txt"
ALLOWED_ROOTS = (
    WORKSPACE_ROOT / "data/dataset_images_labels",
    WORKSPACE_ROOT / "data/dataset_test_train_val",
)


def load_manifest(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            image_il = Path(row["image_il"])
            label_il = Path(row["label_il"])
            image_ttv = Path(row["image_ttv"])
            label_ttv = Path(row["label_ttv"])
            rows.append(
                {
                    "split": row["split"],
                    "class": row["class"],
                    "stem": row["stem"],
                    "filename": image_il.name,
                    "image_url": _media_url(image_il),
                    "label_url": _media_url(label_il),
                    "paths": {
                        "image_il": str(image_il),
                        "label_il": str(label_il),
                        "image_ttv": str(image_ttv),
                        "label_ttv": str(label_ttv),
                    },
                }
            )
    return rows


def load_kept(path: Path, manifest_stems: set[str]) -> set[str]:
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
        return {stem for stem in data.get("kept_stems", []) if stem in manifest_stems}
    return set()


def save_kept(path: Path, kept: set[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "kept_stems": sorted(kept),
        "count": len(kept),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def export_lists(
    keep_path: Path,
    remove_path: Path,
    rows: list[dict],
    kept: set[str],
) -> None:
    by_stem = {row["stem"]: row for row in rows}
    remove_stems = [row["stem"] for row in rows if row["stem"] not in kept]

    keep_lines = ["# Top-down samples to keep in both dataset folders", f"# count: {len(kept)}", ""]
    for stem in sorted(kept):
        row = by_stem[stem]
        keep_lines.append(f"{row['split']}\t{row['class']}\t{stem}\t{row['paths']['image_il']}")
    keep_path.write_text("\n".join(keep_lines) + "\n", encoding="utf-8")

    remove_lines = ["# Samples to remove from both dataset folders", f"# count: {len(remove_stems)}", ""]
    for stem in sorted(remove_stems):
        row = by_stem[stem]
        remove_lines.append(f"{row['split']}\t{row['class']}\t{stem}\t{row['paths']['image_il']}")
    remove_path.write_text("\n".join(remove_lines) + "\n", encoding="utf-8")


def apply_removals(rows: list[dict], kept: set[str], dry_run: bool) -> dict:
    by_stem = {row["stem"]: row for row in rows}
    to_remove = [stem for stem in by_stem if stem not in kept]
    removed_files = 0
    missing_files = 0
    errors: list[str] = []

    for stem in sorted(to_remove):
        row = by_stem[stem]
        for key in ("image_il", "label_il", "image_ttv", "label_ttv"):
            file_path = Path(row["paths"][key])
            if not file_path.is_file():
                missing_files += 1
                continue
            if dry_run:
                removed_files += 1
                continue
            file_path.unlink()
            removed_files += 1

    return {
        "dry_run": dry_run,
        "stems": len(to_remove),
        "kept": len(kept),
        "files_removed": removed_files,
        "files_missing": missing_files,
        "errors": errors,
    }


def _media_url(path: Path) -> str:
    resolved = path.resolve()
    return "/media/" + str(resolved.relative_to(WORKSPACE_ROOT.resolve()))


def _safe_media_path(relative: str) -> Optional[Path]:
    candidate = (WORKSPACE_ROOT / unquote(relative)).resolve()
    if not any(
        root.resolve() in candidate.parents or candidate.resolve() == root.resolve()
        for root in ALLOWED_ROOTS
    ):
        return None
    if not candidate.is_file():
        return None
    return candidate


def _parse_label_boxes(label_path: Path) -> list[dict]:
    boxes: list[dict] = []
    if not label_path.is_file():
        return boxes
    for line in label_path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) != 5:
            continue
        class_id, x_center, y_center, width, height = parts
        boxes.append(
            {
                "class_id": int(class_id),
                "x_center": float(x_center),
                "y_center": float(y_center),
                "width": float(width),
                "height": float(height),
            }
        )
    return boxes


class Handler(BaseHTTPRequestHandler):
    manifest_rows: list[dict] = []
    kept_path: Path = DEFAULT_KEPT
    keep_list_path: Path = DEFAULT_KEEP_LIST
    removal_list_path: Path = DEFAULT_REMOVAL_LIST

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def _manifest_stems(self) -> set[str]:
        return {row["stem"] for row in self.manifest_rows}

    def _kept(self) -> set[str]:
        return load_kept(self.kept_path, self._manifest_stems())

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _send_bytes(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: object, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self._send_bytes(status, body, "application/json; charset=utf-8")

    def _send_file(self, path: Path) -> None:
        content_type, _ = mimetypes.guess_type(str(path))
        content_type = content_type or "application/octet-stream"
        body = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        if path.suffix in {".js", ".html", ".css"}:
            self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _filter_rows(self, query: dict[str, list[str]]) -> list[dict]:
        split = query.get("split", [""])[0]
        class_name = query.get("class", [""])[0]
        show = query.get("show", [""])[0]
        kept = self._kept()

        items = self.manifest_rows
        if split:
            items = [item for item in items if item["split"] == split]
        if class_name:
            items = [item for item in items if item["class"] == class_name]
        if show == "keep":
            items = [item for item in items if item["stem"] in kept]
        elif show == "remove":
            items = [item for item in items if item["stem"] not in kept]
        return items

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        route = parsed.path

        if route in {"/", "/index.html"}:
            return self._send_file(STATIC_DIR / "index.html")
        if route == "/style.css":
            return self._send_file(STATIC_DIR / "style.css")
        if route == "/app.js":
            return self._send_file(STATIC_DIR / "app.js")

        if route == "/api/session":
            query = parse_qs(parsed.query)
            kept = self._kept()
            items = self._filter_rows(query)
            total = len(self.manifest_rows)
            return self._send_json(
                {
                    "items": items,
                    "kept_stems": sorted(kept),
                    "total": total,
                    "kept_count": len(kept),
                    "remove_count": total - len(kept),
                }
            )

        if route == "/api/labels":
            query = parse_qs(parsed.query)
            rel = query.get("path", [""])[0]
            if not rel:
                return self._send_json({"error": "missing path"}, HTTPStatus.BAD_REQUEST)
            match = re.match(r"^media/(.+)$", rel)
            if not match:
                return self._send_json({"error": "invalid path"}, HTTPStatus.BAD_REQUEST)
            label_path = _safe_media_path(match.group(1))
            if label_path is None:
                return self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
            return self._send_json({"boxes": _parse_label_boxes(label_path)})

        if route.startswith("/media/"):
            media_path = _safe_media_path(route.removeprefix("/media/"))
            if media_path is None:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            return self._send_file(media_path)

        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        route = parsed.path

        if route == "/api/keep/set":
            body = self._read_json_body()
            stem = body.get("stem", "")
            keep = bool(body.get("keep", False))
            if not stem:
                return self._send_json({"error": "missing stem"}, HTTPStatus.BAD_REQUEST)
            if stem not in self._manifest_stems():
                return self._send_json({"error": "unknown stem"}, HTTPStatus.BAD_REQUEST)
            kept = self._kept()
            if keep:
                kept.add(stem)
            else:
                kept.discard(stem)
            save_kept(self.kept_path, kept)
            export_lists(self.keep_list_path, self.removal_list_path, self.manifest_rows, kept)
            total = len(self.manifest_rows)
            return self._send_json(
                {
                    "stem": stem,
                    "keep": keep,
                    "kept_count": len(kept),
                    "remove_count": total - len(kept),
                    "total": total,
                    "kept_stems": sorted(kept),
                }
            )

        if route == "/api/keep/reset":
            save_kept(self.kept_path, set())
            export_lists(
                self.keep_list_path,
                self.removal_list_path,
                self.manifest_rows,
                set(),
            )
            total = len(self.manifest_rows)
            return self._send_json(
                {"kept_count": 0, "remove_count": total, "total": total}
            )

        if route == "/api/apply-removals":
            body = self._read_json_body()
            dry_run = bool(body.get("dry_run", True))
            kept = self._kept()
            result = apply_removals(self.manifest_rows, kept, dry_run=dry_run)
            if not dry_run and not result["errors"]:
                removed_stems = {row["stem"] for row in self.manifest_rows} - kept
                self.manifest_rows = [row for row in self.manifest_rows if row["stem"] in kept]
                save_kept(self.kept_path, kept)
                export_lists(
                    self.keep_list_path,
                    self.removal_list_path,
                    self.manifest_rows,
                    kept,
                )
                result["removed_stems"] = len(removed_stems)
            return self._send_json(result)

        self.send_error(HTTPStatus.NOT_FOUND)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review copied pairs: default remove, keep top-down only."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--kept-file", type=Path, default=DEFAULT_KEPT)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    manifest = args.manifest.expanduser().resolve()
    if not manifest.is_file():
        raise SystemExit(f"Manifest not found: {manifest}")

    Handler.manifest_rows = load_manifest(manifest)
    Handler.kept_path = args.kept_file.expanduser().resolve()
    Handler.keep_list_path = Handler.kept_path.parent / "keep_topdown.txt"
    Handler.removal_list_path = Handler.kept_path.parent / "remove_non_topdown.txt"

    stems = {row["stem"] for row in Handler.manifest_rows}
    kept = load_kept(Handler.kept_path, stems)
    export_lists(Handler.keep_list_path, Handler.removal_list_path, Handler.manifest_rows, kept)

    server = None
    port = args.port
    for attempt in range(10):
        try:
            server = ThreadingHTTPServer((args.host, port), Handler)
            break
        except OSError as error:
            if error.errno != 48 or attempt == 9:
                raise
            print(f"Port {port} in use, trying {port + 1}...")
            port += 1

    url = f"http://{args.host}:{port}/"
    print(f"Manifest: {manifest} ({len(Handler.manifest_rows)} items)")
    print(f"Default: remove all except {len(kept)} kept top-down")
    print(f"Open: {url}")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
