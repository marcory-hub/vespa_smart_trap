#!/usr/bin/env python3
"""
Swift-YOLO serial parsing helpers for GV2 benchmark scripts.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class ParsedDetection:
    class_id: int
    confidence: float


@dataclass
class InvokeEvent:
    receipt_time: float
    receipt_time_iso: str
    raw_detections: List[ParsedDetection]
    per_class_max_conf: Dict[int, float]
    unknown_class_ids: List[int]


def epoch_seconds_to_iso(epoch_seconds: float) -> str:
    import datetime as dt

    return dt.datetime.fromtimestamp(epoch_seconds, tz=dt.timezone.utc).isoformat()


def extract_complete_json_objects(buffer: bytearray) -> Tuple[List[bytes], bytearray]:
    """
    Extract complete top-level JSON objects from a mixed serial stream.
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


def parse_invoke_event_strict(
    obj: Dict[str, Any],
    receipt_time: float,
    scoring_class_ids: Sequence[int] = (0, 1, 2, 3),
) -> Tuple[Optional[InvokeEvent], bool]:
    """
    Strict INVOKE parsing.

    Returns:
      (InvokeEvent, False) on success
      (None, True) if object is INVOKE but malformed
      (None, False) if object is not INVOKE
    """
    if obj.get("name") != "INVOKE":
        return None, False

    data = obj.get("data")
    if not isinstance(data, dict):
        return None, True

    boxes = data.get("boxes", [])
    if boxes is None or not isinstance(boxes, list):
        return None, True

    scoring_set = set(int(x) for x in scoring_class_ids)
    raw_detections: List[ParsedDetection] = []
    per_class_max_conf: Dict[int, float] = {}
    unknown_class_ids: List[int] = []

    for box in boxes:
        if not isinstance(box, list) or len(box) < 2:
            return None, True

        raw_conf = box[-2]
        raw_class_id = box[-1]
        try:
            conf = float(raw_conf)
        except (TypeError, ValueError):
            return None, True
        try:
            class_id = int(raw_class_id)
        except (TypeError, ValueError):
            return None, True

        raw_detections.append(ParsedDetection(class_id=class_id, confidence=conf))
        if class_id in scoring_set:
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


def wait_until_ready(serial_conn: Any, ready_timeout_s: float = 20.0) -> None:
    deadline = time.time() + ready_timeout_s
    while time.time() < deadline:
        line = serial_conn.readline()
        if not line:
            continue
        text = line.decode("utf-8", errors="replace")
        if '"name": "MODEL"' in text or '"is_ready": 1' in text:
            return
    raise TimeoutError("Timed out waiting for Swift-YOLO ready status on serial stream.")


def send_at_invoke_and_wait_ready(
    serial_conn: Any,
    result_only: int = 0,
    ready_timeout_s: float = 20.0,
) -> str:
    """
    Wait for ready signal then send AT+INVOKE for infinite inference.
    """
    wait_until_ready(serial_conn=serial_conn, ready_timeout_s=ready_timeout_s)
    command = f"AT+INVOKE=-1,0,{int(result_only)}\r"
    serial_conn.write(command.encode("ascii"))
    return command


def parse_json_objects_from_chunk(
    buffer: bytearray,
    chunk: bytes,
) -> Tuple[List[Dict[str, Any]], bytearray, int]:
    """
    Convenience helper for diagnostics:
    returns (decoded_json_objects, new_buffer, invalid_json_count).
    """
    buffer.extend(chunk)
    objects_raw, remainder = extract_complete_json_objects(buffer)
    decoded: List[Dict[str, Any]] = []
    invalid_json_count = 0
    for raw in objects_raw:
        try:
            obj = json.loads(raw.decode("utf-8", errors="ignore"))
        except Exception:
            invalid_json_count += 1
            continue
        if isinstance(obj, dict):
            decoded.append(obj)
    return decoded, remainder, invalid_json_count
