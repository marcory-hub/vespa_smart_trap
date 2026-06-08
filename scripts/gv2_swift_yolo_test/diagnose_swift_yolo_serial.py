#!/usr/bin/env python3
"""
Diagnose Swift-YOLO GV2 serial output format.

This script verifies:
- whether INVOKE JSON objects are present
- whether `data.boxes` exists and is list-shaped
- whether `data.image` is included when RESULT_ONLY=0
"""

from __future__ import annotations

import argparse
import glob
import time
from typing import Any, Dict, Optional

try:
    import serial  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    serial = None  # type: ignore

from swift_yolo_serial_parser import parse_json_objects_from_chunk, send_at_invoke_and_wait_ready


def resolve_serial_port(explicit_port: Optional[str], serial_port_glob: str) -> str:
    if explicit_port:
        return explicit_port
    matches = sorted(glob.glob(serial_port_glob))
    if not matches:
        raise RuntimeError(f"No serial ports found for glob: {serial_port_glob}")
    if len(matches) > 1:
        raise RuntimeError(
            "Multiple serial ports matched glob; pass --serial-port explicitly. "
            f"Matches: {matches}"
        )
    return matches[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Swift-YOLO serial format diagnostic")
    parser.add_argument("--serial-port", default=None, help="Explicit serial device path.")
    parser.add_argument("--serial-port-glob", default="/dev/tty.usbmodem*", help="Serial port glob fallback.")
    parser.add_argument("--serial-baudrate", type=int, default=921600, help="Serial baudrate.")
    parser.add_argument("--serial-read-timeout", type=float, default=0.2, help="Serial read timeout.")
    parser.add_argument("--ready-timeout-s", type=float, default=20.0, help="Ready wait timeout.")
    parser.add_argument(
        "--capture-seconds",
        type=float,
        default=30.0,
        help="Capture duration after AT+INVOKE is sent.",
    )
    parser.add_argument(
        "--result-only",
        type=int,
        default=0,
        choices=(0, 1),
        help="AT+INVOKE RESULT_ONLY flag. Use 0 to validate image payload.",
    )
    args = parser.parse_args()

    if serial is None:
        raise RuntimeError("pyserial is required (import serial failed).")

    serial_port = resolve_serial_port(explicit_port=args.serial_port, serial_port_glob=args.serial_port_glob)
    print(f"Using serial port: {serial_port}")

    ser = serial.Serial(
        port=serial_port,
        baudrate=args.serial_baudrate,
        timeout=args.serial_read_timeout,
    )
    try:
        try:
            ser.reset_input_buffer()
        except Exception:
            pass

        command = send_at_invoke_and_wait_ready(
            serial_conn=ser,
            result_only=args.result_only,
            ready_timeout_s=args.ready_timeout_s,
        )
        print(f"Sent command: {command.strip()}")

        start = time.time()
        deadline = start + args.capture_seconds
        buffer = bytearray()

        total_json_objects = 0
        invalid_json_objects = 0
        invoke_count = 0
        malformed_invoke_count = 0
        invoke_with_boxes_count = 0
        invoke_with_image_count = 0
        first_invoke_example: Optional[Dict[str, Any]] = None
        first_invoke_data_keys: Optional[list[str]] = None
        first_boxes_example: Optional[Any] = None

        while time.time() < deadline:
            chunk = ser.read(4096)
            if not chunk:
                continue
            decoded_objects, buffer, invalid_count = parse_json_objects_from_chunk(buffer=buffer, chunk=chunk)
            invalid_json_objects += invalid_count
            total_json_objects += len(decoded_objects)

            for obj in decoded_objects:
                if obj.get("name") != "INVOKE":
                    continue
                invoke_count += 1
                if first_invoke_example is None:
                    first_invoke_example = obj
                data = obj.get("data")
                if not isinstance(data, dict):
                    malformed_invoke_count += 1
                    continue
                if first_invoke_data_keys is None:
                    first_invoke_data_keys = sorted(list(data.keys()))

                boxes = data.get("boxes")
                if isinstance(boxes, list):
                    invoke_with_boxes_count += 1
                    if first_boxes_example is None and boxes:
                        first_boxes_example = boxes[0]
                else:
                    malformed_invoke_count += 1

                image_value = data.get("image")
                if isinstance(image_value, str) and bool(image_value.strip()):
                    invoke_with_image_count += 1

        print("\n=== Swift-YOLO Serial Diagnostic Summary ===")
        print(f"capture_seconds: {args.capture_seconds}")
        print(f"result_only: {args.result_only}")
        print(f"json_objects_total: {total_json_objects}")
        print(f"json_objects_invalid: {invalid_json_objects}")
        print(f"invoke_count: {invoke_count}")
        print(f"invoke_malformed_count: {malformed_invoke_count}")
        print(f"invoke_with_boxes_count: {invoke_with_boxes_count}")
        print(f"invoke_with_image_count: {invoke_with_image_count}")
        print(f"first_invoke_data_keys: {first_invoke_data_keys}")
        print(f"first_boxes_example: {first_boxes_example}")
        print("\nVerification guidance:")
        print("- If result_only=0 and invoke_with_image_count > 0, right-pane camera payload is available.")
        print("- If invoke_with_boxes_count == invoke_count, `data.boxes` is structurally present.")
        print("- Class/conf positions inside each box remain [to be verified] and should be checked manually.")
        if first_invoke_example is not None:
            print("\nFirst INVOKE example:")
            print(first_invoke_example)
    finally:
        try:
            ser.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
