#!/usr/bin/env python3
"""
GV2 slideshow set-match experiment (class sets only).

Implements your scoring + logging rules:
- Slideshow: uses `scripts/image_slider_web/server.py` and consumes the first 388 rows from `run_log.csv`.
- Serial: reads live mixed-text serial stream, extracts WE2-style JSON objects with `name == "INVOKE"`.
- Time matching: assigns each accepted INVOKE event to the image frame whose window contains the event receipt timestamp
  using half-open intervals [t0, t0+2.0).
- Scoring: builds predicted class sets from detections with `conf >= 0.30` and compares class sets vs GT sets.
- GT: derived from `data/test/labels/*.txt` with NUL derived from the filename species token.
- Exports: per-image CSV, review_candidates.csv, run_config.json, raw_invoke_events.jsonl, unmatched_invoke_events.jsonl, parse_errors.json.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import glob
import json
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import serial  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    serial = None  # type: ignore


CLASS_ID_TO_NAME: Dict[int, str] = {0: "amel", 1: "vcra", 2: "vespsp", 3: "vvel"}
CLASS_ID_TO_SPECIES_TOKEN: Dict[int, str] = {0: "ame", 1: "vcr", 2: "ves", 3: "vve"}
SCORING_CLASS_IDS: Tuple[int, ...] = (0, 1, 2, 3)
CONFIDENCE_THRESHOLD = 0.30  # inclusive (>=); do not change to strict >
DEFAULT_MANIFEST_SEED = 42

FRAME_DURATION_S = 4.0
GRACE_S = 0.15
SAMPLING_OFFSETS_S: List[float] = [0.5, 1.0, 1.5]
SAMPLING_MATCH_WINDOW_S = 0.200  # +/- 200 ms
SAMPLED_EVENT_START_OFFSET_S = 2.5
SAMPLED_EVENT_STRIDE = 5
SAMPLED_EVENT_COUNT = 3

FILENAME_TOKEN_RE = re.compile(r"^(?P<viewpoint>[a-z]{3})_(?P<species>[A-Za-z]{3})")
VIEWPOINT_TOKENS = {"top", "sid", "oth"}
SPECIES_PREFIX_TOKENS = {"ame", "vcr", "ves", "vve", "NUL"}


def iso_to_epoch_seconds(iso_str: str) -> float:
    # JS uses `new Date().toISOString()` => "...Z" (UTC). Parse it into epoch seconds.
    dt_obj = dt.datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return float(dt_obj.timestamp())


def epoch_seconds_to_iso(epoch_seconds: float) -> str:
    return dt.datetime.fromtimestamp(epoch_seconds, tz=dt.timezone.utc).isoformat()


def parse_image_filename_tokens(image_path: Path) -> Tuple[str, str, bool]:
    match = FILENAME_TOKEN_RE.match(image_path.stem)
    if not match:
        raise ValueError(f"Ambiguous filename (missing vvv_sss prefix): {image_path.name}")

    viewpoint = match.group("viewpoint").lower()
    if viewpoint not in VIEWPOINT_TOKENS:
        raise ValueError(f"Ambiguous filename (invalid viewpoint token): {image_path.name}")

    species_prefix = match.group("species")
    if species_prefix not in SPECIES_PREFIX_TOKENS:
        raise ValueError(f"Ambiguous filename (invalid species token): {image_path.name}")

    return viewpoint, species_prefix, species_prefix == "NUL"


def label_file_path_for_image(image_path: Path, labels_dir: Path) -> Path:
    # image: vvv_sss*.jpg ...; label: sss*.txt ...
    parts = image_path.name.split("_", 1)
    if len(parts) < 2:
        raise ValueError(f"Ambiguous filename: {image_path.name}")
    rest = parts[1]
    if not rest.lower().endswith(".jpg"):
        raise ValueError(f"Ambiguous filename (expected .jpg): {image_path.name}")
    label_name = rest[:-4] + ".txt"
    return labels_dir / label_name


def gt_set_from_label_file(image_path: Path, labels_dir: Path) -> Tuple[set[str], bool]:
    _, species_prefix, is_nul_filename = parse_image_filename_tokens(image_path)
    label_path = label_file_path_for_image(image_path=image_path, labels_dir=labels_dir)

    if not label_path.exists():
        raise FileNotFoundError(f"Missing label file for image: {image_path.name} -> {label_path}")

    raw_text = label_path.read_text(encoding="utf-8").strip()
    lines = raw_text.splitlines() if raw_text else []

    label_class_ids: List[int] = []
    for line in lines:
        if not line.strip():
            continue
        tokens = line.split()
        cid = int(tokens[0])
        label_class_ids.append(cid)

    if is_nul_filename:
        # NUL filename vs label conflict: if the label file is not empty, fail fast.
        if label_class_ids:
            raise ValueError(
                f"NUL filename vs label conflict: {image_path.name} has label class ids {sorted(set(label_class_ids))}"
            )
        return set(), True

    known_ids = [cid for cid in label_class_ids if cid in SCORING_CLASS_IDS]
    unknown_ids = [cid for cid in label_class_ids if cid not in SCORING_CLASS_IDS]

    if len(set(known_ids)) == 0:
        raise ValueError(f"Ambiguous filename (non-NUL but empty/unknown label classes): {image_path.name}")
    if unknown_ids:
        raise ValueError(f"Ambiguous label classes (outside 0..3) for {image_path.name}: {sorted(set(unknown_ids))}")

    gt_set = {CLASS_ID_TO_NAME[cid] for cid in set(known_ids)}
    return gt_set, False


@dataclass(frozen=True)
class ParsedDetection:
    class_id: int
    confidence: float


@dataclass
class InvokeEvent:
    receipt_time: float
    receipt_time_iso: str
    raw_detections: List[ParsedDetection]
    per_class_max_conf: Dict[int, float]  # only for scoring classes 0..3
    unknown_class_ids: List[int]  # for logging only


def extract_complete_json_objects(buffer: bytearray) -> Tuple[List[bytes], bytearray]:
    """
    Extract complete top-level JSON objects from a byte stream.

    Serial stream is mixed text; locate objects by balanced '{' / '}' nesting outside strings.
    """
    objects: List[bytes] = []
    last_consumed_index = 0

    start_index: Optional[int] = None
    depth = 0
    in_string = False
    escape = False

    i = 0
    while i < len(buffer):
        b = buffer[i]

        if start_index is None:
            if b == ord("{"):
                start_index = i
                depth = 1
                in_string = False
                escape = False
            i += 1
            continue

        if in_string:
            if escape:
                escape = False
            elif b == ord("\\"):
                escape = True
            elif b == ord('"'):
                in_string = False
        else:
            if b == ord('"'):
                in_string = True
            elif b == ord("{"):
                depth += 1
            elif b == ord("}"):
                depth -= 1
                if depth == 0 and start_index is not None:
                    end_index = i + 1
                    objects.append(bytes(buffer[start_index:end_index]))
                    last_consumed_index = end_index
                    start_index = None
                    depth = 0
                    in_string = False
                    escape = False

        i += 1

    remaining = buffer[last_consumed_index:]
    return objects, remaining


def parse_invoke_event_strict(obj: Dict[str, Any], receipt_time: float) -> Tuple[Optional[InvokeEvent], bool]:
    """
    Strict INVOKE parsing.

    Rejects partially malformed INVOKE objects entirely:
    - if `data.boxes` isn't a list, reject.
    - if any box entry is malformed (wrong structure / conf not float / class id not int), reject the whole INVOKE.
    """
    if obj.get("name") != "INVOKE":
        return None, False

    data = obj.get("data")
    if not isinstance(data, dict):
        return None, True

    boxes = data.get("boxes", [])
    if boxes is None or not isinstance(boxes, list):
        return None, True

    raw_detections: List[ParsedDetection] = []
    per_class_max_conf: Dict[int, float] = {}
    unknown_class_ids: List[int] = []

    for b in boxes:
        if not isinstance(b, list) or len(b) < 2:
            return None, True

        raw_conf = b[-2]
        raw_class_id = b[-1]

        try:
            conf = float(raw_conf)
        except (TypeError, ValueError):
            return None, True

        try:
            class_id = int(raw_class_id)
        except (TypeError, ValueError):
            return None, True

        raw_detections.append(ParsedDetection(class_id=class_id, confidence=conf))

        if class_id in SCORING_CLASS_IDS:
            prev = per_class_max_conf.get(class_id)
            if prev is None or conf > prev:
                per_class_max_conf[class_id] = conf
        else:
            unknown_class_ids.append(class_id)

    receipt_time_iso = epoch_seconds_to_iso(receipt_time)
    return (
        InvokeEvent(
            receipt_time=receipt_time,
            receipt_time_iso=receipt_time_iso,
            raw_detections=raw_detections,
            per_class_max_conf=per_class_max_conf,
            unknown_class_ids=unknown_class_ids,
        ),
        False,
    )


def choose_nearest_event_for_sampling(
    assigned_events: List[InvokeEvent],
    sample_time: float,
    class_id: int,
) -> Optional[Tuple[InvokeEvent, float]]:
    candidates: List[Tuple[float, float, InvokeEvent]] = []
    for ev in assigned_events:
        if class_id not in ev.per_class_max_conf:
            continue
        delta = abs(ev.receipt_time - sample_time)
        if delta <= SAMPLING_MATCH_WINDOW_S:
            candidates.append((delta, ev.receipt_time, ev))

    if not candidates:
        return None

    candidates.sort(key=lambda t: (t[0], t[1]))
    best_delta, _, best_ev = candidates[0]
    return best_ev, best_delta


def resolve_git_commit(repo_root: Path) -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception:
        return None
    sha = result.stdout.strip()
    return sha or None


def post_latest_inference(slider_port: int, species: str, confidence: float, at_iso: str) -> None:
    payload = json.dumps(
        {
            "species": species,
            "confidence": float(confidence),
            "at_iso": at_iso,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        url=f"http://127.0.0.1:{slider_port}/log/inference",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=0.25):
            pass
    except Exception:
        # UI feedback channel is best-effort and must not interrupt scoring.
        return


def post_camera_frame(slider_port: int, image_base64: str, at_iso: str) -> None:
    payload = json.dumps(
        {
            "image_base64": image_base64,
            "at_iso": at_iso,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        url=f"http://127.0.0.1:{slider_port}/log/camera_frame",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=0.25):
            pass
    except Exception:
        # Camera preview channel is best-effort and must not interrupt scoring.
        return


def wait_for_slider_ready(slider_port: int, timeout_seconds: float = 5.0) -> None:
    deadline = time.time() + timeout_seconds
    last_error: Optional[str] = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{slider_port}/manifest.json?shuffle=1&seed={DEFAULT_MANIFEST_SEED}",
                timeout=0.5,
            ):
                return
        except Exception as exc:
            last_error = str(exc)
            time.sleep(0.1)
    raise TimeoutError(f"Timed out waiting for slider server readiness on port {slider_port}: {last_error}")


def run() -> None:
    parser = argparse.ArgumentParser(description="GV2 slideshow serial set-match experiment (class sets only).")
    parser.add_argument("--model-name", default=None, help="Flashed model name string (output folder naming).")
    parser.add_argument("--slider-port", type=int, default=8000, help="Port for scripts/image_slider_web/server.py")
    parser.add_argument("--expected-count", type=int, default=388, help="Expected number of images to score.")
    parser.add_argument(
        "--serial-port",
        default=None,
        help="Explicit serial device path (recommended). If omitted, --serial-port-glob is used.",
    )
    parser.add_argument("--serial-port-glob", default="/dev/tty.usbmodem*", help="Serial port glob (macOS).")
    parser.add_argument("--serial-baudrate", type=int, default=921600, help="GV2 serial baudrate.")
    parser.add_argument("--serial-read-timeout", type=float, default=0.2, help="GV2 serial read timeout.")
    parser.add_argument(
        "--slider-wait-runlog-seconds",
        type=float,
        default=0.0,
        help="Wait for slider run_log.csv. <=0 disables timeout.",
    )
    parser.add_argument(
        "--sampled-avg-threshold",
        type=float,
        default=CONFIDENCE_THRESHOLD,
        help="Primary avg-confidence threshold for sampled-event set membership.",
    )
    parser.add_argument(
        "--sampled-avg-threshold-opt",
        type=float,
        default=None,
        help="Optional secondary avg-confidence threshold (e.g., F1-optimal) for transition logging.",
    )
    parser.add_argument(
        "--sampling-start-offset-s",
        type=float,
        default=SAMPLED_EVENT_START_OFFSET_S,
        help="Start sampled-event selection this many seconds after frame start.",
    )
    parser.add_argument(
        "--sampling-event-stride",
        type=int,
        default=SAMPLED_EVENT_STRIDE,
        help="Sample stride in event indices (e.g., 5 picks events 0,5,10...).",
    )
    parser.add_argument(
        "--sampling-event-count",
        type=int,
        default=SAMPLED_EVENT_COUNT,
        help="Number of sampled events to use for avg-confidence scoring.",
    )
    parser.add_argument("--skip-open-browser", action="store_true", help="Do not open browser.")
    parser.add_argument(
        "--locked-benchmark",
        action="store_true",
        help="Enable strict slider benchmark mode (manual controls disabled).",
    )
    args = parser.parse_args()

    if serial is None:
        raise RuntimeError("pyserial is required (import serial failed).")
    if args.sampling_event_stride <= 0:
        raise ValueError("sampling-event-stride must be > 0")
    if args.sampling_event_count <= 0:
        raise ValueError("sampling-event-count must be > 0")
    if args.sampling_start_offset_s < 0:
        raise ValueError("sampling-start-offset-s must be >= 0")

    repo_root = Path(__file__).resolve().parents[2]
    slider_dir = repo_root / "scripts" / "image_slider_web"
    slider_server_script = slider_dir / "server.py"
    slider_outputs_dir = slider_dir / "outputs"

    images_dir = repo_root / "data" / "test" / "images"
    labels_dir = repo_root / "data" / "test" / "labels"

    if not images_dir.exists():
        raise FileNotFoundError(f"Missing images dir: {images_dir}")
    if not labels_dir.exists():
        raise FileNotFoundError(f"Missing labels dir: {labels_dir}")

    model_name = args.model_name or input("Enter flashed model name string: ").strip()
    if not model_name:
        raise ValueError("model-name must not be empty.")

    run_timestamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_root = repo_root / "outputs"
    out_root.mkdir(parents=True, exist_ok=True)
    out_dir = out_root / f"{run_timestamp}__{model_name}"
    out_dir.mkdir(parents=False, exist_ok=False)

    # Serial port selection.
    serial_selection_mode = "explicit" if args.serial_port else "glob"
    if args.serial_port:
        serial_port = args.serial_port
        if not Path(serial_port).exists():
            raise RuntimeError(f"Specified serial port does not exist: {serial_port}")
    else:
        serial_ports = sorted(glob.glob(args.serial_port_glob))
        if not serial_ports:
            raise RuntimeError(f"No serial ports found for glob: {args.serial_port_glob}")
        if len(serial_ports) > 1:
            raise RuntimeError(
                "Multiple serial ports matched glob; pass --serial-port explicitly. "
                f"Matches: {serial_ports}"
            )
        serial_port = serial_ports[0]

    run_config = {
        "model_name": model_name,
        "host_timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "tooling": {
            "python_executable": sys.executable,
            "python_version": sys.version,
            "git_commit": resolve_git_commit(repo_root),
        },
        "expected_count": args.expected_count,
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "sampled_avg_threshold_primary": args.sampled_avg_threshold,
        "sampled_avg_threshold_opt": args.sampled_avg_threshold_opt,
        "frame_duration_s": FRAME_DURATION_S,
        "grace_s": GRACE_S,
        "sampling_start_offset_s": args.sampling_start_offset_s,
        "sampling_event_stride": args.sampling_event_stride,
        "sampling_event_count": args.sampling_event_count,
        "sampling_offsets_legacy_s": SAMPLING_OFFSETS_S,
        "sampling_match_window_legacy_s": SAMPLING_MATCH_WINDOW_S,
        "frame_rule": f"half-open [t0,t0+{FRAME_DURATION_S:.1f})",
        "timeout_policy": "timeout_flag=1 iff no accepted INVOKE events were assigned to the frame",
        "serial_port_selection_mode": serial_selection_mode,
        "serial_port_resolved": serial_port,
        "serial_port_glob": args.serial_port_glob,
        "serial_baudrate": args.serial_baudrate,
        "serial_read_timeout_s": args.serial_read_timeout,
        "serial_assignment": "assign only if receipt_time is inside frame half-open interval",
        "unknown_class_id_handling": "ignore classes outside 0..3 for scoring; keep in raw logs",
        "nul_handling": "NUL gt derived from filename species token; background scoring uses empty sets",
        "slider": {
            "slider_port": args.slider_port,
            "default_manifest_order": "shuffle",
            "default_manifest_seed": DEFAULT_MANIFEST_SEED,
            "locked_benchmark_requested": bool(args.locked_benchmark),
        },
    }
    frame_collection_timeout_seconds: Optional[float] = None
    run_config["frame_collection_timeout_seconds"] = frame_collection_timeout_seconds
    run_config_path = out_dir / "run_config.json"
    run_config_path.write_text(json.dumps(run_config, indent=2), encoding="utf-8")

    # Start slider server (so run_log.csv is produced).
    if slider_outputs_dir.exists():
        before_run_folders = {p.name for p in slider_outputs_dir.iterdir() if p.is_dir()}
    else:
        slider_outputs_dir.mkdir(parents=True, exist_ok=True)
        before_run_folders = set()

    # Resources initialised before the try/finally so both are always reachable in the finally block.
    ser = None
    slider_stderr_fh = (out_dir / "slider_server.log").open("w", encoding="utf-8")
    slider_command = ["python3", str(slider_server_script), "--port", str(args.slider_port)]
    if args.locked_benchmark:
        slider_command.append("--locked-benchmark")
    slider_process = subprocess.Popen(
        slider_command,
        cwd=str(slider_dir),
        stdout=subprocess.DEVNULL,
        stderr=slider_stderr_fh,
    )
    time.sleep(0.2)
    if slider_process.poll() is not None:
        raise RuntimeError(
            "Failed to start slider server process. "
            f"See {out_dir / 'slider_server.log'} for details."
        )
    wait_for_slider_ready(slider_port=args.slider_port, timeout_seconds=5.0)

    try:
        if not args.skip_open_browser:
            slider_url = f"http://127.0.0.1:{args.slider_port}/?shuffle=1&seed={DEFAULT_MANIFEST_SEED}"
            if args.locked_benchmark:
                slider_url = f"{slider_url}&benchmark=1"
            webbrowser.open(slider_url)

        # Wait for a new run folder with run_log.csv.
        run_dir: Optional[Path] = None
        runlog_deadline: Optional[float] = None
        if args.slider_wait_runlog_seconds > 0:
            runlog_deadline = time.time() + args.slider_wait_runlog_seconds
        while run_dir is None:
            for p in slider_outputs_dir.iterdir():
                if not p.is_dir():
                    continue
                if p.name in before_run_folders:
                    continue
                candidate = p / "run_log.csv"
                if candidate.exists() and candidate.is_file():
                    run_dir = p
                    break
            if run_dir is None:
                if runlog_deadline is not None and time.time() >= runlog_deadline:
                    raise TimeoutError("Timed out waiting for slider run_log.csv.")
                time.sleep(0.25)

        run_log_path = run_dir / "run_log.csv"
        control_events_path = run_dir / "control_events.jsonl"
        run_meta_path = run_dir / "run_meta.json"
        inference_events_path = run_dir / "inference_events.jsonl"
        slider_meta: Dict[str, Any] = {}
        if run_meta_path.exists():
            try:
                slider_meta = json.loads(run_meta_path.read_text(encoding="utf-8"))
            except Exception:
                slider_meta = {"_warning": "failed to parse slider run_meta.json"}
        run_config["slider"]["run_id"] = run_dir.name
        run_config["slider"]["run_log_path"] = str(run_log_path.relative_to(repo_root))
        run_config["slider"]["control_events_path"] = str(control_events_path.relative_to(repo_root))
        run_config["slider"]["run_meta_path"] = str(run_meta_path.relative_to(repo_root))
        run_config["slider"]["inference_events_path"] = str(inference_events_path.relative_to(repo_root))
        run_config["slider"]["run_meta"] = slider_meta
        run_config_path.write_text(json.dumps(run_config, indent=2), encoding="utf-8")

        # Start serial capture.
        ser = serial.Serial(port=serial_port, baudrate=args.serial_baudrate, timeout=args.serial_read_timeout)  # type: ignore[attr-defined]  # noqa: E501
        try:
            ser.reset_input_buffer()
        except Exception:
            pass

        invoke_events: List[InvokeEvent] = []
        unmatched_events: List[InvokeEvent] = []
        parse_errors: List[Dict[str, Any]] = []
        parse_error_count = 0
        parse_error_invoke_count = 0

        lock = threading.Lock()
        stop_event = threading.Event()
        buffer = bytearray()
        last_camera_frame_post_time = 0.0

        def serial_thread_body() -> None:
            nonlocal buffer, parse_error_count, parse_error_invoke_count, last_camera_frame_post_time
            while not stop_event.is_set():
                try:
                    chunk = ser.read(4096)
                except Exception:
                    break
                if not chunk:
                    continue

                buffer.extend(chunk)
                objects, buffer_remaining = extract_complete_json_objects(buffer)
                buffer = buffer_remaining

                for obj_bytes in objects:
                    # Capture receipt_time before decode so timing is as close to arrival as possible.
                    receipt_time = time.time()
                    try:
                        decoded = obj_bytes.decode("utf-8", errors="ignore")
                        parsed_obj = json.loads(decoded)
                    except Exception:
                        parse_error_count += 1
                        if b"INVOKE" in obj_bytes:
                            parse_error_invoke_count += 1
                            with lock:
                                parse_errors.append(
                                    {"receipt_time_iso": epoch_seconds_to_iso(receipt_time), "reason": "invalid_json"}
                                )
                        continue

                    if not isinstance(parsed_obj, dict):
                        continue
                    if parsed_obj.get("name") != "INVOKE":
                        continue
                    parsed_data = parsed_obj.get("data")
                    if isinstance(parsed_data, dict):
                        image_base64 = parsed_data.get("image")
                        if isinstance(image_base64, str) and image_base64:
                            if receipt_time - last_camera_frame_post_time >= 0.40:
                                post_camera_frame(
                                    slider_port=args.slider_port,
                                    image_base64=image_base64,
                                    at_iso=epoch_seconds_to_iso(receipt_time),
                                )
                                last_camera_frame_post_time = receipt_time

                    invoke_event, invalid = parse_invoke_event_strict(parsed_obj, receipt_time)
                    if invalid or invoke_event is None:
                        parse_error_count += 1
                        parse_error_invoke_count += 1
                        with lock:
                            parse_errors.append(
                                {
                                    "receipt_time_iso": epoch_seconds_to_iso(receipt_time),
                                    "reason": "invalid_invoke_event",
                                }
                            )
                        continue

                    with lock:
                        invoke_events.append(invoke_event)
                    if invoke_event.per_class_max_conf:
                        best_class_id = max(
                            invoke_event.per_class_max_conf.keys(),
                            key=lambda class_id: invoke_event.per_class_max_conf[class_id],
                        )
                        best_confidence = invoke_event.per_class_max_conf[best_class_id]
                        species_token = CLASS_ID_TO_SPECIES_TOKEN.get(best_class_id, "nul")
                    else:
                        species_token = "nul"
                        best_confidence = 0.0
                    post_latest_inference(
                        slider_port=args.slider_port,
                        species=species_token,
                        confidence=best_confidence,
                        at_iso=invoke_event.receipt_time_iso,
                    )

        serial_thread = threading.Thread(target=serial_thread_body, daemon=True)
        serial_thread.start()

        # Wait for the first expected_count rows to be written by the slideshow.
        frames_rows: List[Dict[str, str]] = []
        while True:
            if run_log_path.exists():
                with run_log_path.open("r", newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                if len(rows) >= args.expected_count:
                    frames_rows = rows[: args.expected_count]
                    break
            time.sleep(0.25)

        # Build frames from slider timestamps.
        frames: List[Dict[str, Any]] = []
        for idx, row in enumerate(frames_rows):
            shown_at_iso = row.get("shown_at_iso", "")
            if not shown_at_iso:
                raise ValueError("Missing shown_at_iso in slider log row.")
            t0 = iso_to_epoch_seconds(shown_at_iso)
            frames.append(
                {
                    "frame_index": idx,
                    "t0": t0,
                    "t0_iso": shown_at_iso,
                    "filename": row["filename"],
                }
            )

        frames.sort(key=lambda f: f["t0"])
        t0s = [f["t0"] for f in frames]

        last_frame_t0 = frames[-1]["t0"]
        serial_stop_time = last_frame_t0 + FRAME_DURATION_S + GRACE_S
        while time.time() < serial_stop_time:
            time.sleep(0.05)

        stop_event.set()
        serial_thread.join(timeout=5.0)
        try:
            ser.close()
        except Exception:
            pass

        with lock:
            invoke_events_snapshot = sorted(list(invoke_events), key=lambda ev: ev.receipt_time)

        # Assign events to frames using half-open ownership windows.
        for f in frames:
            f["assigned_invoke_events"] = []

        t0_end = [t0 + FRAME_DURATION_S for t0 in t0s]

        for ev in invoke_events_snapshot:
            te = ev.receipt_time
            i = bisect_right(t0s, te) - 1
            assigned = False

            for ci in (i, i + 1):
                if 0 <= ci < len(frames):
                    if te >= t0s[ci] and te < t0_end[ci]:
                        frames[ci]["assigned_invoke_events"].append(ev)
                        assigned = True
                        break

            if not assigned:
                unmatched_events.append(ev)

        # Scoring: GT sets and predicted sets.
        per_class_tp: Dict[str, int] = {CLASS_ID_TO_NAME[cid]: 0 for cid in SCORING_CLASS_IDS}
        per_class_fp: Dict[str, int] = {CLASS_ID_TO_NAME[cid]: 0 for cid in SCORING_CLASS_IDS}
        per_class_fn: Dict[str, int] = {CLASS_ID_TO_NAME[cid]: 0 for cid in SCORING_CLASS_IDS}

        exact_set_match_count = 0
        per_image_rows: List[Dict[str, Any]] = []
        review_candidate_rows: List[Dict[str, Any]] = []

        for frame in frames:
            image_path = images_dir / frame["filename"]

            gt_set, is_nul_gt = gt_set_from_label_file(image_path=image_path, labels_dir=labels_dir)
            assigned_events: List[InvokeEvent] = frame["assigned_invoke_events"]
            timeout_flag = 1 if len(assigned_events) == 0 else 0

            # Transition logging set #1: any-window membership (legacy behavior).
            pred_set_any_window: set[str] = set()
            raw_detections_frame: List[Dict[str, Any]] = []
            for ev in assigned_events:
                raw_detections_frame.append(
                    {
                        "receipt_time_iso": ev.receipt_time_iso,
                        "detections": [
                            {"class_id": det.class_id, "confidence": det.confidence} for det in ev.raw_detections
                        ],
                        "unknown_class_ids": sorted(set(ev.unknown_class_ids)),
                    }
                )

                for class_id in SCORING_CLASS_IDS:
                    max_conf = ev.per_class_max_conf.get(class_id)
                    if max_conf is not None and max_conf >= CONFIDENCE_THRESHOLD:
                        pred_set_any_window.add(CLASS_ID_TO_NAME[class_id])

            # New scoring set: sampled events start at t0+offset, then stride by event index.
            eligible_events = [ev for ev in assigned_events if ev.receipt_time >= (frame["t0"] + args.sampling_start_offset_s)]
            sampled_event_indices: List[int] = []
            sampled_events: List[InvokeEvent] = []
            next_index = 0
            for _ in range(args.sampling_event_count):
                if next_index >= len(eligible_events):
                    break
                sampled_event_indices.append(next_index)
                sampled_events.append(eligible_events[next_index])
                next_index += args.sampling_event_stride

            sampled_event_debug = [
                {"eligible_index": idx, "receipt_time_iso": ev.receipt_time_iso}
                for idx, ev in zip(sampled_event_indices, sampled_events)
            ]

            sample_avg_conf_by_class: Dict[str, Optional[float]] = {}
            pred_set_sampled_avg_primary: set[str] = set()
            pred_set_sampled_avg_opt: set[str] = set()
            for class_id in SCORING_CLASS_IDS:
                class_name = CLASS_ID_TO_NAME[class_id]
                conf_samples: List[float] = []
                for ev in sampled_events:
                    conf_val = ev.per_class_max_conf.get(class_id)
                    if conf_val is not None:
                        conf_samples.append(conf_val)

                avg_conf = (sum(conf_samples) / len(conf_samples)) if conf_samples else None
                sample_avg_conf_by_class[class_name] = avg_conf
                if avg_conf is not None and avg_conf >= args.sampled_avg_threshold:
                    pred_set_sampled_avg_primary.add(class_name)
                if args.sampled_avg_threshold_opt is not None and avg_conf is not None and avg_conf >= args.sampled_avg_threshold_opt:
                    pred_set_sampled_avg_opt.add(class_name)

            match_exact = pred_set_sampled_avg_primary == gt_set
            if match_exact:
                exact_set_match_count += 1
                match_type = "complete"
            else:
                match_type = "partial" if pred_set_sampled_avg_primary.intersection(gt_set) else "no_match"

            multi_species_flag = 1 if (len(gt_set) > 1 or len(pred_set_sampled_avg_primary) > 1) else 0

            # Per-class presence-based TP/FP/FN.
            for class_id in SCORING_CLASS_IDS:
                class_name = CLASS_ID_TO_NAME[class_id]
                gt_has = class_name in gt_set
                pred_has = class_name in pred_set_sampled_avg_primary
                if gt_has and pred_has:
                    per_class_tp[class_name] += 1
                elif pred_has and not gt_has:
                    per_class_fp[class_name] += 1
                elif gt_has and not pred_has:
                    per_class_fn[class_name] += 1

            row = {
                "frame_index": frame["frame_index"],
                "shown_at_iso": frame["t0_iso"],
                "image_filename": frame["filename"],
                "gt_is_nul": int(is_nul_gt),
                "gt_set": json.dumps(sorted(gt_set)),
                "pred_set_sampled_avg": json.dumps(sorted(pred_set_sampled_avg_primary)),
                "pred_set_any_window": json.dumps(sorted(pred_set_any_window)),
                "pred_set_sampled_avg_opt": json.dumps(sorted(pred_set_sampled_avg_opt)),
                "exact_match": int(match_exact),
                "match_type": match_type,
                "timeout_flag": int(timeout_flag),
                "multi_species_flag": int(multi_species_flag),
                "sample_count_used": len(sampled_events),
                "sampled_event_debug": json.dumps(sampled_event_debug),
                "raw_detections_frame": json.dumps(raw_detections_frame),
                "sample_avg_conf_by_class": json.dumps(sample_avg_conf_by_class),
                "sample_rule": (
                    f"start_offset={args.sampling_start_offset_s}s; "
                    f"stride={args.sampling_event_stride}; count={args.sampling_event_count}"
                ),
            }
            per_image_rows.append(row)

            if (not match_exact) or multi_species_flag == 1 or timeout_flag == 1:
                review_candidate_rows.append(row)

        # Write per-image exports.
        if not per_image_rows:
            raise RuntimeError("No per-image rows were produced; check GT parsing and frame assignment.")
        per_image_csv_path = out_dir / "per_image_results.csv"
        fieldnames = list(per_image_rows[0].keys())
        with per_image_csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in per_image_rows:
                writer.writerow(r)

        review_csv_path = out_dir / "review_candidates.csv"
        with review_csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in review_candidate_rows:
                writer.writerow(r)

        # Write raw invoke logs and unmatched events.
        raw_invoke_events_path = out_dir / "raw_invoke_events.jsonl"
        with raw_invoke_events_path.open("w", encoding="utf-8") as f:
            for ev in invoke_events_snapshot:
                f.write(
                    json.dumps(
                        {
                            "receipt_time_iso": ev.receipt_time_iso,
                            "receipt_time": ev.receipt_time,
                            "detections": [
                                {"class_id": det.class_id, "confidence": det.confidence} for det in ev.raw_detections
                            ],
                            "unknown_class_ids": sorted(set(ev.unknown_class_ids)),
                        }
                    )
                    + "\n"
                )

        unmatched_events_path = out_dir / "unmatched_invoke_events.jsonl"
        with unmatched_events_path.open("w", encoding="utf-8") as f:
            for ev in sorted(unmatched_events, key=lambda e: e.receipt_time):
                f.write(
                    json.dumps(
                        {
                            "receipt_time_iso": ev.receipt_time_iso,
                            "receipt_time": ev.receipt_time,
                            "detections": [
                                {"class_id": det.class_id, "confidence": det.confidence} for det in ev.raw_detections
                            ],
                            "unknown_class_ids": sorted(set(ev.unknown_class_ids)),
                        }
                    )
                    + "\n"
                )

        # Write parse errors.
        parse_errors_path = out_dir / "parse_errors.json"
        parse_errors_path.write_text(
            json.dumps(
                {
                    "parse_error_count": parse_error_count,
                    "parse_error_invoke_count": parse_error_invoke_count,
                    "errors": parse_errors,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        # Per-class precision/recall diagnostics.
        per_class_metrics_csv_path = out_dir / "per_class_metrics.csv"
        with per_class_metrics_csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["class_name", "TP", "FP", "FN", "support_gt_images", "precision", "recall"],
            )
            writer.writeheader()
            for class_id in SCORING_CLASS_IDS:
                class_name = CLASS_ID_TO_NAME[class_id]
                tp = per_class_tp[class_name]
                fp = per_class_fp[class_name]
                fn = per_class_fn[class_name]
                precision_denom = tp + fp
                recall_denom = tp + fn

                precision = "NA" if precision_denom == 0 else f"{tp / precision_denom:.6f}"
                recall = "NA" if recall_denom == 0 else f"{tp / recall_denom:.6f}"
                support = tp + fn

                writer.writerow(
                    {
                        "class_name": class_name,
                        "TP": tp,
                        "FP": fp,
                        "FN": fn,
                        "support_gt_images": support,
                        "precision": precision,
                        "recall": recall,
                    }
                )

        # Final summary printing.
        overall_exact_set_match_rate = exact_set_match_count / float(args.expected_count)
        print(
            f"Overall exact set match rate: {overall_exact_set_match_rate:.6f} "
            f"({exact_set_match_count}/{args.expected_count})"
        )
        print(f"Total INVOKE events received: {len(invoke_events_snapshot)}")
        print(f"Unmatched INVOKE events (outside all frame windows): {len(unmatched_events)}")
        print(f"Parse errors: {parse_error_count} total, {parse_error_invoke_count} INVOKE-related")

        for class_id in SCORING_CLASS_IDS:
            class_name = CLASS_ID_TO_NAME[class_id]
            tp = per_class_tp[class_name]
            fp = per_class_fp[class_name]
            fn = per_class_fn[class_name]
            precision_denom = tp + fp
            recall_denom = tp + fn
            precision = "NA" if precision_denom == 0 else f"{tp / precision_denom:.6f}"
            recall = "NA" if recall_denom == 0 else f"{tp / recall_denom:.6f}"
            support = tp + fn
            print(f"{class_name}: TP={tp} FP={fp} FN={fn} support={support} precision={precision} recall={recall}")

    finally:
        try:
            slider_process.terminate()
        except Exception:
            pass
        if ser is not None:
            try:
                ser.close()
            except Exception:
                pass
        if slider_stderr_fh is not None:
            try:
                slider_stderr_fh.close()
            except Exception:
                pass


if __name__ == "__main__":
    run()

