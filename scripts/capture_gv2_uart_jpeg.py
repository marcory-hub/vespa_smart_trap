#!/usr/bin/env python3
"""
Capture a single JPEG frame from the ESP32 USB serial output.

Expected stream format (from experiments/gv2_uart_esp32_led):
  recv #<n> len=<bytes> state=<...> class=<...> conf_u8=<...> conf=<...>\n
  <raw JPEG payload bytes, exactly len bytes>

Usage (replace XXXX with the number of your ESP32 port number, can be found with `ls /dev/cu.usbmodem*`):
  python3 scripts/capture_gv2_uart_jpeg.py /dev/cu.usbmodemXXXX 115200

Output:
  Writes frame_XXXX.jpg in the current directory.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    try:
        import serial  # type: ignore
    except Exception as e:  # pragma: no cover
        print("Missing dependency: pyserial", file=sys.stderr)
        print("Install with: python3 -m pip install pyserial", file=sys.stderr)
        print(f"Import error: {e}", file=sys.stderr)
        return 2

    port = sys.argv[1] if len(sys.argv) > 1 else "/dev/cu.usbmodem1101"
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 115200

    # Example header:
    # recv #1 len=3488 state=0 class=3 conf_u8=146 conf=0.573
    hdr_re = re.compile(rb"^recv #(\d+)\s+len=(\d+)\b")

    ser = serial.Serial(port, baud, timeout=2)
    try:
        while True:
            line = ser.readline()
            if not line:
                continue

            m = hdr_re.match(line.strip())
            if not m:
                continue

            idx = int(m.group(1))
            n = int(m.group(2))

            data = ser.read(n)
            if len(data) != n:
                print(f"incomplete frame: got {len(data)}/{n} bytes", file=sys.stderr)
                continue

            out = Path(f"frame_{idx:04d}.jpg")
            out.write_bytes(data)
            print(f"saved {out} ({n} bytes)")
            return 0
    finally:
        ser.close()


if __name__ == "__main__":
    raise SystemExit(main())

