#!/usr/bin/env python3
"""
GV2 YOLO serial-only benchmark runner.

This runner:
- shows each image to a physical camera via a local slideshow HTTP server
- reads mixed serial output and extracts JSON objects
- keeps only WE2-style JSON objects with name="INVOKE"
- performs class-only evaluation against filename-derived ground truth
- exports per-image results to CSV and prints confusion-matrix + metrics
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    import serial  # type: ignore
except ModuleNotFoundError as e:
    serial = None  # type: ignore

try:
    import requests  # type: ignore
except ModuleNotFoundError as e:
    requests = None  # type: ignore


CLASS_ID_TO_NAME: Dict[int, str] = {0: "amel", 1: "vcra", 2: "vesp", 3: "vvel"}


@dataclass
class Prediction:
    predicted_class_id: Optional[int]
    score: Optional[float]


def parse_filename_ground_truth(image_path: Path) -> Tuple[Optional[int], str]:
    """
    Ground truth is derived from filename.

    Expected naming (plan):
      <view>_<label>_<id>.jpg

    Actual dataset filenames observed here look like:
      <view>_<label>_<id>_jpg.rf.<hash>.jpg
    where label variants include amel1/amel2, vcra1/vcra2, vespsp1/vespsp2, vvel1/vvel2, NULL.
    """

    stem = image_path.stem  # removes only the final ".jpg"
    parts = stem.split("_")
    if len(parts) < 2:
        # Keep the runner running even if naming is unexpected.
        return None, "unknown"

    view_token = parts[0].strip().lower()
    label_token = parts[1].strip().lower()

    if view_token not in {"top", "sid", "oth"}:
        # Still return view_token; metrics will just be aggregated under "unknown".
        view_token = "unknown"

    if label_token.startswith("null"):
        return None, view_token
    if label_token.startswith("amel"):
        return 0, view_token
    if label_token.startswith("vcra"):
        return 1, view_token
    if label_token.startswith("vesp"):
        # Handles both "vesp" and the observed "vespsp".
        return 2, view_token
    if label_token.startswith("vvel"):
        return 3, view_token

    # Unknown label variant -> treat as NULL to avoid contaminating class metrics.
    return None, view_token


def deterministic_image_list(images_dir: Path, expected_count: int, seed: int) -> List[Path]:
    images = sorted(images_dir.glob("*.jpg"))
    if len(images) != expected_count:
        print(
            f"WARNING: Found {len(images)} images in {images_dir}, expected {expected_count}. "
            "Proceeding with found set.",
            file=sys.stderr,
        )
    rng = random.Random(seed)
    rng.shuffle(images)
    return images


def extract_complete_json_objects(buffer: bytearray) -> Tuple[List[bytes], bytearray]:
    """
    Extract complete top-level JSON objects from a byte stream.

    The serial stream is mixed text; we locate objects by:
    - first '{' start
    - balanced nesting of '{' / '}' outside JSON strings
    - returns remaining bytes after the last complete object
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

        # We are inside a candidate JSON object.
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
                if depth == 0:
                    # Complete object.
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


def wait_for_latest_invoke(
    ser: Any,
    timeout_seconds: float,
) -> Optional[Dict[str, Any]]:
    """
    Read until timeout and return the most recent JSON object with name="INVOKE".
    Returns the decoded dict (latest seen), or None if timeout is reached without any INVOKE.
    """

    deadline = time.time() + timeout_seconds
    buffer = bytearray()
    last_invoke: Optional[Dict[str, Any]] = None

    while time.time() < deadline:
        try:
            # Timeout is handled by the serial object; this read should not block forever.
            chunk = ser.read(4096)
        except serial.SerialException as e:  # type: ignore[name-defined]
            # Caller will decide how to stop; re-raise so we can exit cleanly.
            raise RuntimeError(f"Serial read failed (device likely disconnected): {e}") from e

        if not chunk:
            continue

        buffer.extend(chunk)
        objects, buffer = extract_complete_json_objects(buffer)

        for obj_bytes in objects:
            try:
                obj = json.loads(obj_bytes.decode("utf-8", errors="ignore"))
            except json.JSONDecodeError:
                continue

            if not isinstance(obj, dict):
                continue

            if obj.get("name") != "INVOKE":
                continue

            # Defensive: remove image field if present (we do not need it for evaluation).
            data = obj.get("data")
            if isinstance(data, dict) and "image" in data:
                # This does not shrink the already-parsed string, but ensures we don't carry it further.
                data.pop("image", None)

            last_invoke = obj

    return last_invoke


def parse_prediction_from_invoke(invoke: Optional[Dict[str, Any]], confidence_threshold: Optional[float]) -> Prediction:
    if not invoke:
        return Prediction(predicted_class_id=None, score=None)

    data = invoke.get("data", {})
    if not isinstance(data, dict):
        return Prediction(predicted_class_id=None, score=None)

    boxes = data.get("boxes", [])
    if not isinstance(boxes, list) or not boxes:
        return Prediction(predicted_class_id=None, score=None)

    best_score: Optional[float] = None
    best_class: Optional[int] = None

    for b in boxes:
        if not isinstance(b, list) or len(b) < 2:
            continue
        raw_score = b[-2]
        raw_class = b[-1]

        try:
            score = float(raw_score)
        except (TypeError, ValueError):
            continue

        try:
            class_id = int(raw_class)
        except (TypeError, ValueError):
            continue

        if class_id not in (0, 1, 2, 3):
            continue

        if best_score is None or score > best_score:
            best_score = score
            best_class = class_id

    if best_score is None or best_class is None:
        return Prediction(predicted_class_id=None, score=None)

    if confidence_threshold is not None and best_score < confidence_threshold:
        return Prediction(predicted_class_id=None, score=best_score)

    return Prediction(predicted_class_id=best_class, score=best_score)


def show_image_via_slideshow(slideshow_url: str, image_path: Path) -> None:
    if requests is None:
        raise RuntimeError("requests is not available in this Python environment.")

    url = slideshow_url.rstrip("/")
    endpoint = f"{url}/show"

    payload = {
        "image_path": str(image_path),
        "filename": image_path.name,
    }
    try:
        resp = requests.post(endpoint, json=payload, timeout=5)
        resp.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"Failed to POST to slideshow endpoint {endpoint}: {e}") from e


def print_confusion_matrix(confusion: List[List[int]]) -> None:
    class_names = [CLASS_ID_TO_NAME[i] for i in range(4)]

    # Header
    header = ["GT\\Pred"] + class_names
    col_widths = [max(len(h), 10) for h in header]

    def fmt_row(items: Iterable[str]) -> str:
        return " ".join(str(x).rjust(w) for x, w in zip(items, col_widths))

    print(fmt_row(header))
    for gt in range(4):
        row = [class_names[gt]]
        row.extend(str(confusion[gt][pred]) for pred in range(4))
        print(fmt_row(row))


def safe_div(n: float, d: float) -> float:
    if d == 0:
        return 0.0
    return n / d


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark GV2 serial INVOKE outputs over a fixed test image set.")
    parser.add_argument("--model-name", default=None, help="Model name string used in CSV filename (prompt if omitted).")
    parser.add_argument("--images-dir", default="data/test/images", help="Folder containing .jpg test images.")
    parser.add_argument("--expected-count", type=int, default=388, help="Expected number of images.")
    parser.add_argument("--seed", type=int, default=42, help="Seed for deterministic random shuffle.")
    parser.add_argument("--serial-port", default="/dev/tty.usbmodem58FA1047631", help="GV2 serial port.")
    parser.add_argument("--baudrate", type=int, default=921600, help="GV2 serial baudrate.")
    parser.add_argument("--serial-timeout", type=float, default=0.2, help="Serial read timeout (seconds).")
    parser.add_argument("--invoke-timeout", type=float, default=8.0, help="How long to wait per image for an INVOKE message.")
    parser.add_argument("--confidence-threshold", type=float, default=None, help="Optional confidence threshold; no threshold if omitted.")
    parser.add_argument("--slideshow-url", default="http://localhost:8000", help="Local slideshow server base URL.")
    parser.add_argument("--first-image-wait-seconds", type=float, default=30.0, help="Wait after first /show.")
    parser.add_argument("--next-image-wait-seconds", type=float, default=1.0, help="Wait after each subsequent /show.")
    parser.add_argument("--skip-slideshow", action="store_true", help="Skip /show calls; useful for headless debugging.")

    args = parser.parse_args()

    model_name = args.model_name
    if not model_name:
        model_name = input("Enter model name string: ").strip()
    if not model_name:
        print("ERROR: model-name must not be empty.", file=sys.stderr)
        sys.exit(2)

    images_dir = Path(args.images_dir).expanduser().resolve()
    if not images_dir.exists():
        print(f"ERROR: images-dir does not exist: {images_dir}", file=sys.stderr)
        sys.exit(2)

    images = deterministic_image_list(images_dir, args.expected_count, args.seed)

    if serial is None:
        print("ERROR: pyserial (import serial) is not available in this environment.", file=sys.stderr)
        sys.exit(2)

    # Metrics for 4 classes (0..3). We track NULL ground truth separately via FP/FN logic.
    confusion = [[0 for _ in range(4)] for _ in range(4)]
    tp = [0 for _ in range(4)]
    fp = [0 for _ in range(4)]
    fn = [0 for _ in range(4)]
    total_gt = [0 for _ in range(4)]

    view_labels = ["top", "sid", "oth"]
    tp_view: Dict[str, List[int]] = {v: [0 for _ in range(4)] for v in view_labels}
    fp_view: Dict[str, List[int]] = {v: [0 for _ in range(4)] for v in view_labels}
    fn_view: Dict[str, List[int]] = {v: [0 for _ in range(4)] for v in view_labels}
    total_gt_view: Dict[str, int] = {v: 0 for v in view_labels}
    correct_view: Dict[str, int] = {v: 0 for v in view_labels}

    results: List[Dict[str, Any]] = []

    csv_out_path = Path(__file__).resolve().parent / f"results_{model_name}.csv"
    print(f"Writing CSV: {csv_out_path}")

    print(f"Opening serial port {args.serial_port} @ {args.baudrate}...")
    ser = None
    try:
        ser = serial.Serial(  # type: ignore[attr-defined]
            port=args.serial_port,
            baudrate=args.baudrate,
            timeout=args.serial_timeout,
        )
    except Exception as e:
        print(f"ERROR: Could not open serial port {args.serial_port}: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        for idx, image_path in enumerate(images):
            gt_class_id, view = parse_filename_ground_truth(image_path)

            # Flush input before triggering the next image so we do not accidentally
            # parse an INVOKE from the previous iteration.
            try:
                ser.reset_input_buffer()
            except Exception:
                try:
                    ser.flushInput()
                except Exception:
                    pass

            if not args.skip_slideshow:
                show_image_via_slideshow(args.slideshow_url, image_path)

            # Timing rule from plan.
            if idx == 0:
                time.sleep(args.first_image_wait_seconds)
            else:
                time.sleep(args.next_image_wait_seconds)

            try:
                invoke = wait_for_latest_invoke(ser, timeout_seconds=args.invoke_timeout)
            except RuntimeError as e:
                # Likely: unplugged serial device.
                print(str(e), file=sys.stderr)
                break

            prediction = parse_prediction_from_invoke(invoke, args.confidence_threshold)

            pred_class_id = prediction.predicted_class_id

            # Update metrics (4-class evaluation only).
            # If GT is NULL/background, we export the row to CSV but do not include it
            # in the 4x4 confusion matrix or per-class metrics.
            if gt_class_id is not None:
                total_gt[gt_class_id] += 1

                if pred_class_id == gt_class_id:
                    if view in view_labels:
                        total_gt_view[view] += 1
                        correct_view[view] += 1
                        tp_view[view][gt_class_id] += 1
                    tp[gt_class_id] += 1
                    confusion[gt_class_id][gt_class_id] += 1
                else:
                    if view in view_labels:
                        total_gt_view[view] += 1
                        fn_view[view][gt_class_id] += 1
                    # Predicted something else (or nothing) for a non-NULL GT class.
                    fn[gt_class_id] += 1
                    if pred_class_id is not None:
                        fp[pred_class_id] += 1
                        confusion[gt_class_id][pred_class_id] += 1
                        if view in view_labels:
                            fp_view[view][pred_class_id] += 1

            gt_label = CLASS_ID_TO_NAME[gt_class_id] if gt_class_id is not None else "NULL"
            pred_label = CLASS_ID_TO_NAME[pred_class_id] if pred_class_id is not None else "No Detection"
            score_str = "" if prediction.score is None else f"{prediction.score:.6g}"

            if pred_class_id is None:
                result = "No Detection"
            elif gt_class_id is None:
                result = "False Positive"
            elif pred_class_id == gt_class_id:
                result = "Correct"
            else:
                result = "Misclassified"

            results.append(
                {
                    "Image_Path": str(image_path),
                    "Ground_Truth": gt_label,
                    "Predicted": pred_label,
                    "Score": score_str,
                    "Result": result,
                }
            )

            if (idx + 1) % 10 == 0:
                print(f"Processed {idx + 1}/{len(images)} images...")

    except KeyboardInterrupt:
        print("Interrupted by user; writing partial results CSV...", file=sys.stderr)
    except Exception as e:
        print(f"ERROR during benchmarking: {e}", file=sys.stderr)
    finally:
        try:
            if ser is not None:
                ser.close()
        except Exception:
            pass

    # Export CSV (always attempt).
    fieldnames = ["Image_Path", "Ground_Truth", "Predicted", "Score", "Result"]
    try:
        with csv_out_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"ERROR writing CSV: {e}", file=sys.stderr)

    # Print confusion + metrics.
    print_confusion_matrix(confusion)

    total_correct = sum(tp)
    total_for_accuracy = sum(total_gt)
    overall_accuracy = safe_div(float(total_correct), float(total_for_accuracy))
    print(f"Overall accuracy (non-NULL GT, 4 classes): {overall_accuracy:.4f} ({total_correct}/{total_for_accuracy})")

    print("\nPer-class metrics:")
    for class_id in range(4):
        precision = safe_div(float(tp[class_id]), float(tp[class_id] + fp[class_id]))
        recall = safe_div(float(tp[class_id]), float(tp[class_id] + fn[class_id]))
        tn = float(total_for_accuracy - tp[class_id] - fp[class_id] - fn[class_id])
        class_accuracy = safe_div(float(tp[class_id]) + tn, float(total_for_accuracy))
        print(
            f"- {CLASS_ID_TO_NAME[class_id]}: "
            f"accuracy={class_accuracy:.4f} precision={precision:.4f} recall={recall:.4f} "
            f"(TP={tp[class_id]} FP={fp[class_id]} FN={fn[class_id]} TN={int(tn)})"
        )

    print("\nView metrics (non-NULL GT only):")
    for view in view_labels:
        total = total_gt_view.get(view, 0)
        correct = correct_view.get(view, 0)
        if total == 0:
            continue

        # Macro-average precision/recall across the 4 object classes for this view slice.
        precisions: List[float] = []
        recalls: List[float] = []
        for class_id in range(4):
            tp_c = tp_view[view][class_id]
            fp_c = fp_view[view][class_id]
            fn_c = fn_view[view][class_id]
            precisions.append(safe_div(float(tp_c), float(tp_c + fp_c)))
            recalls.append(safe_div(float(tp_c), float(tp_c + fn_c)))
        view_precision = sum(precisions) / 4.0
        view_recall = sum(recalls) / 4.0
        view_accuracy = safe_div(float(correct), float(total))

        print(
            f"- {view}: accuracy={view_accuracy:.4f} precision={view_precision:.4f} recall={view_recall:.4f} "
            f"({correct}/{total})"
        )


if __name__ == "__main__":
    main()

