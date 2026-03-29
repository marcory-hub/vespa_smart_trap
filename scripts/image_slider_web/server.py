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
import statistics
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
LABELS_DIR = WORKSPACE_ROOT / "data" / "test" / "labels"
OUTPUTS_DIR = Path(__file__).resolve().parent / "outputs"
RUNS_LEDGER_PATH = Path(__file__).resolve().parent / "runs_ledger.jsonl"

INTRO_TEXT = "Setup preview: align camera framing, then press Space to start."
DEFAULT_MANIFEST_SEED = 42

VIEWPOINT_TOKENS = {"oth", "sid", "top"}
SPECIES_TOKENS = {"ame", "vcr", "ves", "vve", "NUL"}
CLASS_ID_TO_SPECIES_TOKEN = {0: "ame", 1: "vcr", 2: "ves", 3: "vve"}
SPECIES_AVERAGE_LENGTH_CM = {"ame": 1.25, "vcr": 3.00, "ves": 1.30, "vve": 2.50}
DISPLAY_WIDTH_MIN_CM = 4.0
DISPLAY_WIDTH_MAX_CM = 30.0

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


def _label_file_path_for_image_name(image_name: str) -> Path:
    parts = image_name.split("_", 1)
    if len(parts) < 2:
        raise ValueError(f"ambiguous image name: {image_name}")
    rest = parts[1]
    if not rest.lower().endswith(".jpg"):
        raise ValueError(f"expected .jpg image name: {image_name}")
    return LABELS_DIR / f"{rest[:-4]}.txt"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _compute_species_body_norm_from_labels() -> dict[str, float]:
    by_species: dict[str, list[float]] = {token: [] for token in CLASS_ID_TO_SPECIES_TOKEN.values()}
    for label_path in sorted(LABELS_DIR.glob("*.txt")):
        raw_text = label_path.read_text(encoding="utf-8").strip()
        if not raw_text:
            continue
        for line in raw_text.splitlines():
            tokens = line.strip().split()
            if len(tokens) < 5:
                continue
            try:
                class_id = int(tokens[0])
                box_width_norm = float(tokens[3])
                box_height_norm = float(tokens[4])
            except ValueError:
                continue
            species_token = CLASS_ID_TO_SPECIES_TOKEN.get(class_id)
            if species_token is None:
                continue
            body_norm = max(box_width_norm, box_height_norm)
            if body_norm > 0:
                by_species[species_token].append(body_norm)
    medians: dict[str, float] = {}
    for species_token, values in by_species.items():
        if values:
            medians[species_token] = float(statistics.median(values))
    return medians


def _image_body_norm_for_species(image_name: str, species_token: str) -> Optional[float]:
    label_path = _label_file_path_for_image_name(image_name)
    if not label_path.exists():
        return None
    raw_text = label_path.read_text(encoding="utf-8").strip()
    if not raw_text:
        return None
    target_class_id = None
    for class_id, token in CLASS_ID_TO_SPECIES_TOKEN.items():
        if token == species_token:
            target_class_id = class_id
            break
    if target_class_id is None:
        return None
    values: list[float] = []
    for line in raw_text.splitlines():
        tokens = line.strip().split()
        if len(tokens) < 5:
            continue
        try:
            class_id = int(tokens[0])
            box_width_norm = float(tokens[3])
            box_height_norm = float(tokens[4])
        except ValueError:
            continue
        if class_id != target_class_id:
            continue
        body_norm = max(box_width_norm, box_height_norm)
        if body_norm > 0:
            values.append(body_norm)
    if not values:
        return None
    return float(statistics.median(values))


@dataclass(frozen=True)
class ManifestItem:
    index: int
    filename: str
    url: str
    viewpoint: str
    species: str
    display_width_cm: float


@dataclass
class CurrentRun:
    run_id: str
    run_dir: Path
    log_path: Path
    control_events_path: Path
    run_meta_path: Path
    inference_events_path: Path


class SliderServerState:
    def __init__(self) -> None:
        self._current_run: Optional[CurrentRun] = None
        self._locked_benchmark = False
        self._latest_inference: Optional[dict[str, Any]] = None
        self._latest_camera_frame: Optional[dict[str, Any]] = None

    @staticmethod
    def _run_log_has_image_rows(log_path: Path) -> bool:
        if not log_path.exists():
            return False
        with log_path.open("r", encoding="utf-8") as f:
            # Header only means run not started yet from scoring perspective.
            _header = f.readline()
            second_line = f.readline()
        return bool(second_line.strip())

    def set_locked_benchmark(self, locked_benchmark: bool) -> None:
        self._locked_benchmark = locked_benchmark

    def locked_benchmark(self) -> bool:
        return self._locked_benchmark

    def start_new_run(self) -> CurrentRun:
        # Idempotent behavior for setup/reload race:
        # if a run already exists but no image rows are logged yet, reuse it.
        if self._current_run is not None:
            try:
                if not self._run_log_has_image_rows(self._current_run.log_path):
                    return self._current_run
            except Exception:
                # Fall through to creating a new run if current run metadata is unreadable.
                pass

        timestamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        run_dir = OUTPUTS_DIR / timestamp
        run_dir.mkdir(parents=True, exist_ok=False)
        log_path = run_dir / "run_log.csv"
        control_events_path = run_dir / "control_events.jsonl"
        run_meta_path = run_dir / "run_meta.json"
        inference_events_path = run_dir / "inference_events.jsonl"
        with log_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["index", "filename", "viewpoint", "species", "shown_at_iso"])
        run_meta_path.write_text(
            json.dumps(
                {
                    "run_id": timestamp,
                    "started_at_iso": _iso_now(),
                    "locked_benchmark": self._locked_benchmark,
                    "manifest_default_order": "shuffle",
                    "manifest_default_seed": DEFAULT_MANIFEST_SEED,
                    "manifest_shuffle_supported": True,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        run = CurrentRun(
            run_id=timestamp,
            run_dir=run_dir,
            log_path=log_path,
            control_events_path=control_events_path,
            run_meta_path=run_meta_path,
            inference_events_path=inference_events_path,
        )
        ledger_row = {
            "run_id": timestamp,
            "started_at_iso": _iso_now(),
            "locked_benchmark": self._locked_benchmark,
            "run_log_path": str(log_path.relative_to(WORKSPACE_ROOT)),
            "run_meta_path": str(run_meta_path.relative_to(WORKSPACE_ROOT)),
            "control_events_path": str(control_events_path.relative_to(WORKSPACE_ROOT)),
            "inference_events_path": str(inference_events_path.relative_to(WORKSPACE_ROOT)),
        }
        with RUNS_LEDGER_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(ledger_row) + "\n")
        self._current_run = run
        self._latest_inference = None
        self._latest_camera_frame = None
        return run

    def current_run(self) -> Optional[CurrentRun]:
        return self._current_run

    def set_latest_inference(self, payload: dict[str, Any]) -> None:
        self._latest_inference = payload

    def latest_inference(self) -> Optional[dict[str, Any]]:
        return self._latest_inference

    def set_latest_camera_frame(self, payload: dict[str, Any]) -> None:
        self._latest_camera_frame = payload

    def latest_camera_frame(self) -> Optional[dict[str, Any]]:
        return self._latest_camera_frame


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
            return self._handle_manifest(query_string=parsed.query)
        if path == "/api/latest_inference":
            return self._handle_latest_inference()
        if path == "/api/latest_camera_frame":
            return self._handle_latest_camera_frame()
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
        if path == "/log/control":
            return self._handle_control_log()
        if path == "/log/inference":
            return self._handle_inference_log()
        if path == "/log/camera_frame":
            return self._handle_camera_frame_log()
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
                "run_meta_path": str(run.run_meta_path.relative_to(WORKSPACE_ROOT)),
                "control_events_path": str(run.control_events_path.relative_to(WORKSPACE_ROOT)),
                "inference_events_path": str(run.inference_events_path.relative_to(WORKSPACE_ROOT)),
                "locked_benchmark": STATE.locked_benchmark(),
                "intro_text": INTRO_TEXT,
            },
        )

    def _handle_manifest(self, query_string: str) -> None:
        if not IMAGES_DIR.exists():
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": "images directory does not exist", "path": str(IMAGES_DIR)},
            )
            return

        params = urllib.parse.parse_qs(query_string)
        shuffle_enabled = False
        shuffle_values = params.get("shuffle")
        if shuffle_values:
            shuffle_raw = shuffle_values[-1]
            shuffle_enabled = shuffle_raw.strip().lower() in {"1", "true", "yes", "on"}
        seed_value: Optional[int] = None
        seed_values = params.get("seed")
        if seed_values:
            try:
                seed_value = int(seed_values[-1])
            except ValueError:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid seed (must be integer)"})
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
        shuffle_seed = DEFAULT_MANIFEST_SEED if seed_value is None else seed_value
        ordered_names = _seeded_shuffle(sorted_names, seed=shuffle_seed) if shuffle_enabled else sorted_names

        token_map = {name: (viewpoint, species) for (name, viewpoint, species) in parsed}
        species_norm_defaults = _compute_species_body_norm_from_labels()
        items: list[ManifestItem] = []
        for idx, filename in enumerate(ordered_names, start=1):
            viewpoint, species = token_map[filename]
            display_width_cm = 8.0
            if species in SPECIES_AVERAGE_LENGTH_CM:
                image_body_norm = _image_body_norm_for_species(filename, species)
                species_body_norm = (
                    image_body_norm
                    if image_body_norm is not None
                    else species_norm_defaults.get(species)
                )
                if species_body_norm is not None and species_body_norm > 0:
                    target_body_cm = SPECIES_AVERAGE_LENGTH_CM[species]
                    display_width_cm = _clamp(
                        target_body_cm / species_body_norm,
                        DISPLAY_WIDTH_MIN_CM,
                        DISPLAY_WIDTH_MAX_CM,
                    )
            items.append(
                ManifestItem(
                    index=idx,
                    filename=filename,
                    url=f"/images/{urllib.parse.quote(filename)}",
                    viewpoint=viewpoint,
                    species=species,
                    display_width_cm=round(display_width_cm, 3),
                )
            )

        self._send_json(
            HTTPStatus.OK,
            {
                "count": len(items),
                "seed": shuffle_seed if shuffle_enabled else None,
                "items": [item.__dict__ for item in items],
            },
        )

    def _handle_latest_inference(self) -> None:
        self._send_json(HTTPStatus.OK, {"latest_inference": STATE.latest_inference()})

    def _handle_latest_camera_frame(self) -> None:
        self._send_json(HTTPStatus.OK, {"latest_camera_frame": STATE.latest_camera_frame()})

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

    def _handle_control_log(self) -> None:
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

        event_name = payload.get("event")
        event_at_iso = payload.get("at_iso")
        if not isinstance(event_name, str) or not event_name:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "missing or invalid event"})
            return
        if not isinstance(event_at_iso, str) or not event_at_iso:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "missing or invalid at_iso"})
            return

        event_row = {
            "event": event_name,
            "at_iso": event_at_iso,
            "locked_benchmark": STATE.locked_benchmark(),
        }
        with run.control_events_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event_row) + "\n")

        self._send_json(HTTPStatus.OK, {"ok": True})

    def _handle_inference_log(self) -> None:
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

        required = {"species", "confidence", "at_iso"}
        missing = sorted(required - set(payload.keys()))
        if missing:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "missing fields", "missing": missing})
            return

        species = payload.get("species")
        confidence = payload.get("confidence")
        at_iso = payload.get("at_iso")
        if not isinstance(species, str) or not species:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid species"})
            return
        if not isinstance(at_iso, str) or not at_iso:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid at_iso"})
            return
        try:
            confidence_float = float(confidence)
        except (TypeError, ValueError):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid confidence"})
            return

        row = {"species": species, "confidence": confidence_float, "at_iso": at_iso}
        with run.inference_events_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
        STATE.set_latest_inference(row)
        self._send_json(HTTPStatus.OK, {"ok": True})

    def _handle_camera_frame_log(self) -> None:
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

        required = {"image_base64", "at_iso"}
        missing = sorted(required - set(payload.keys()))
        if missing:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "missing fields", "missing": missing})
            return

        image_base64 = payload.get("image_base64")
        at_iso = payload.get("at_iso")
        if not isinstance(image_base64, str) or not image_base64:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid image_base64"})
            return
        if not isinstance(at_iso, str) or not at_iso:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid at_iso"})
            return

        STATE.set_latest_camera_frame({"image_base64": image_base64, "at_iso": at_iso})
        self._send_json(HTTPStatus.OK, {"ok": True})


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Local image slider web server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument(
        "--locked-benchmark",
        action="store_true",
        help="Disable manual slideshow controls for strict benchmark runs.",
    )
    args = parser.parse_args(argv[1:])

    host = args.host
    port = args.port
    STATE.set_locked_benchmark(args.locked_benchmark)

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
