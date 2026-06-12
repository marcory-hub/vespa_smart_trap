#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import datetime as dt
import errno
import json
import os
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


CLASS_ID_TO_NAME: Dict[int, str] = {0: "amel", 1: "vcra", 2: "vesp", 3: "vvel"}

BOX_COLORS_BGR: Dict[int, Tuple[int, int, int]] = {
    0: (0, 255, 0),
    1: (0, 255, 255),
    2: (0, 255, 0),
    3: (0, 0, 255),
}
DEFAULT_BOX_COLOR_BGR = (0, 255, 255)
DISPLAY_WINDOW_NAME = "GV2 detections"
MAX_SERIAL_BUFFER_BYTES = 2 * 1024 * 1024
MAX_SERIAL_READ_BYTES = 262144
DEFAULT_DISPLAY_FPS = 15.0
BACKLOG_BUFFER_BYTES = 16384
STALL_RECONNECT_SECONDS = 20.0
OPEN_GRACE_SECONDS = 12.0
USB_RESET_BOOT_SECONDS = 2.5
INVOKE_MESSAGE_MARKER = b'\r{"type": 1, "name": "INVOKE"'


@dataclass(frozen=True)
class DetectionBox:
    x: int
    y: int
    width: int
    height: int
    score: float
    class_id: int

    @property
    def class_name(self) -> str:
        return CLASS_ID_TO_NAME.get(self.class_id, f"class{self.class_id}")


def extract_complete_json_objects(buffer: bytearray) -> Tuple[List[bytes], bytearray]:
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
                if depth == 0:
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


def parse_detection_box(raw_box: List[Any]) -> Optional[DetectionBox]:
    if not isinstance(raw_box, list) or len(raw_box) < 6:
        return None

    try:
        x = int(raw_box[0])
        y = int(raw_box[1])
        width = int(raw_box[2])
        height = int(raw_box[3])
        class_id = int(raw_box[-1])
    except (TypeError, ValueError):
        return None

    try:
        score = float(raw_box[-2])
    except (TypeError, ValueError):
        return None

    if score > 1.0:
        # GV2 JSON box scores are already converted to integer percent by firmware.
        score = score / 100.0

    return DetectionBox(
        x=x,
        y=y,
        width=width,
        height=height,
        score=score,
        class_id=class_id,
    )


def parse_detection_boxes(invoke: Dict[str, Any]) -> List[DetectionBox]:
    data = invoke.get("data")
    if not isinstance(data, dict):
        return []

    boxes = data.get("boxes")
    if not isinstance(boxes, list):
        return []

    parsed: List[DetectionBox] = []
    for raw_box in boxes:
        if not isinstance(raw_box, list):
            continue
        box = parse_detection_box(raw_box)
        if box is not None:
            parsed.append(box)
    return parsed


def parse_best_box(invoke: Dict[str, Any]) -> Tuple[Optional[int], Optional[float]]:
    boxes = parse_detection_boxes(invoke)
    if not boxes:
        return None, None

    best = max(boxes, key=lambda box: box.score)
    return best.class_id, best.score


def decode_jpeg_image(jpg: bytes) -> Optional[Any]:
    import cv2
    import numpy as np

    arr = np.frombuffer(jpg, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        return None
    return image


def encode_jpeg_image(image: Any) -> Optional[bytes]:
    import cv2

    ok, encoded = cv2.imencode(".jpg", image)
    if not ok:
        return None
    return encoded.tobytes()


def save_jpeg_with_boxes(jpg: bytes, boxes: List[DetectionBox], path: Path) -> bool:
    image = decode_jpeg_image(jpg)
    if image is None:
        return False
    annotated = draw_detection_boxes(image, boxes)
    encoded = encode_jpeg_image(annotated)
    if encoded is None:
        return False
    path.write_bytes(encoded)
    return True


def draw_detection_boxes(image: Any, boxes: List[DetectionBox]) -> Any:
    import cv2

    canvas = image.copy()
    for box in boxes:
        x1 = box.x
        y1 = box.y
        x2 = box.x + box.width
        y2 = box.y + box.height
        color = BOX_COLORS_BGR.get(box.class_id, DEFAULT_BOX_COLOR_BGR)
        cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 2)
        label = f"{box.class_name} {box.score:.2f}"
        text_y = max(y1 - 8, 16)
        cv2.putText(
            canvas,
            label,
            (x1, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1,
            cv2.LINE_AA,
        )
    return canvas


def make_status_frame(lines: List[str]) -> Any:
    import cv2
    import numpy as np

    canvas = np.zeros((240, 320, 3), dtype=np.uint8)
    y = 36
    for line in lines:
        cv2.putText(
            canvas,
            line,
            (12, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (220, 220, 220),
            1,
            cv2.LINE_AA,
        )
        y += 28
    return canvas


def init_opencv_window(window_name: str) -> None:
    import cv2

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 640, 480)
    cv2.imshow(
        window_name,
        make_status_frame(["GV2 detections", "Waiting for serial data..."]),
    )
    cv2.waitKey(1)


def drop_stale_invoke_messages(buffer: bytearray, *, keep_tail_bytes: int = BACKLOG_BUFFER_BYTES) -> int:
    """Discard older INVOKE payloads when the host falls behind (prevents GV2 UART TX stall)."""
    if len(buffer) <= keep_tail_bytes:
        return 0

    marker_index = buffer.rfind(INVOKE_MESSAGE_MARKER)
    if marker_index > 0:
        discarded = marker_index
        del buffer[:marker_index]
        return discarded

    discarded = len(buffer) - keep_tail_bytes
    del buffer[:-keep_tail_bytes]
    return discarded


def trim_oversized_serial_buffer(buffer: bytearray, max_bytes: int) -> bool:
    if len(buffer) <= max_bytes:
        return False

    marker_index = buffer.rfind(INVOKE_MESSAGE_MARKER)
    if marker_index > 0:
        del buffer[:marker_index]
    else:
        start_index = buffer.rfind(b"{")
        if start_index > 0:
            del buffer[:start_index]
        else:
            buffer.clear()
    return True


def decode_jpeg_from_invoke(invoke: Dict[str, Any]) -> Optional[bytes]:
    data = invoke.get("data")
    if not isinstance(data, dict):
        return None
    img_b64 = data.get("image")
    if not isinstance(img_b64, str) or not img_b64:
        return None
    payload = img_b64.strip()
    if payload.startswith("data:") and "," in payload:
        payload = payload.split(",", 1)[1]
    try:
        return base64.b64decode(payload, validate=False)
    except Exception:
        return None


def play_chime(sound_path: str) -> None:
    try:
        subprocess.run(
            ["afplay", sound_path],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except Exception:
        return


def safe_class_name(class_id: Optional[int]) -> str:
    if class_id is None:
        return "none"
    name = CLASS_ID_TO_NAME.get(class_id, f"class{class_id}")
    return "".join(c for c in name if c.isalnum() or c in ("-", "_")).strip("_-") or f"class{class_id}"


def _is_serial_disconnect(exc: BaseException, serial_mod: Any) -> bool:
    errnos = {errno.ENXIO, errno.EIO, errno.ENODEV, errno.ENOENT}
    chain: Optional[BaseException] = exc
    seen: set[int] = set()
    while chain is not None and id(chain) not in seen:
        seen.add(id(chain))
        if isinstance(chain, OSError) and chain.errno in errnos:
            return True
        chain = chain.__cause__ or chain.__context__

    if isinstance(exc, serial_mod.SerialException):
        msg = str(exc).lower()
        if "device not configured" in msg or "errno 6" in msg:
            return True
        if "input/output error" in msg or "errno 5" in msg:
            return True
        if "no such device" in msg or "errno 19" in msg:
            return True
        if "no such file" in msg or "errno 2" in msg:
            return True
    return False


def _safe_close_serial(ser: Any) -> None:
    if ser is None:
        return
    try:
        ser.close()
    except Exception:
        pass


def _chain_has_errno(exc: BaseException, want: int) -> bool:
    chain: Optional[BaseException] = exc
    seen: set[int] = set()
    while chain is not None and id(chain) not in seen:
        seen.add(id(chain))
        if isinstance(chain, OSError) and chain.errno == want:
            return True
        chain = chain.__cause__ or chain.__context__
    return False


def pulse_usb_reset(port: str, baudrate: int, *, boot_seconds: float) -> None:
    """Toggle DTR/RTS so a GV2 stuck in blocking uart_write can reboot its USB stack."""
    try:
        import serial  # type: ignore
    except Exception:
        return

    try:
        probe = serial.Serial(port, baudrate, timeout=0.2)
        try:
            probe.dtr = False
            probe.rts = False
            time.sleep(0.15)
            probe.dtr = True
            probe.rts = True
        finally:
            probe.close()
    except Exception:
        pass

    if boot_seconds > 0:
        time.sleep(boot_seconds)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=os.environ.get("GV2_PORT", "/dev/tty.usbmodem58FA1047631"))
    parser.add_argument("--baudrate", type=int, default=int(os.environ.get("GV2_BAUD", "921600")))
    parser.add_argument("--serial-timeout", type=float, default=0.05)

    parser.add_argument("--save-dir", default=str(Path(__file__).resolve().parent / "images"))
    parser.add_argument("--save-fps", type=float, default=2.0)
    parser.add_argument("--save-threshold", type=float, default=0.3)

    parser.add_argument("--chime-threshold", type=float, default=0.3)
    parser.add_argument("--chime-cooldown-seconds", type=float, default=2.0)
    parser.add_argument("--sound", default="/System/Library/Sounds/Glass.aiff")
    parser.add_argument(
        "--reconnect-delay",
        type=float,
        default=0.5,
        help="Seconds to wait before retrying open/read after a transient serial error.",
    )
    parser.add_argument(
        "--reconnect-log-interval",
        type=float,
        default=10.0,
        help="Minimum seconds between identical reconnect warnings (0 = log every retry).",
    )
    parser.add_argument(
        "--display",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Show live camera frames with bounding boxes in an OpenCV window (default: on).",
    )
    parser.add_argument(
        "--display-min-score",
        type=float,
        default=0.75,
        help="Only draw boxes at or above this confidence in the display window.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Log INVOKE diagnostics to stderr.",
    )
    parser.add_argument(
        "--status-interval",
        type=float,
        default=3.0,
        help="Print serial/display heartbeat to stderr every N seconds (0=off).",
    )
    parser.add_argument(
        "--display-fps",
        type=float,
        default=DEFAULT_DISPLAY_FPS,
        help="Max OpenCV refresh rate (default: 15).",
    )
    parser.add_argument(
        "--stall-reconnect-seconds",
        type=float,
        default=STALL_RECONNECT_SECONDS,
        help="Recover serial if no bytes arrive for this many seconds (default: 20).",
    )
    parser.add_argument(
        "--open-grace-seconds",
        type=float,
        default=OPEN_GRACE_SECONDS,
        help="After opening serial, wait this long before stall recovery (default: 12).",
    )
    parser.add_argument(
        "--no-usb-reset",
        action="store_true",
        help="Skip DTR/RTS USB reset during stall recovery.",
    )

    args = parser.parse_args()

    try:
        import serial  # type: ignore
    except Exception as e:
        print("Missing dependency: pyserial", file=sys.stderr)
        print("Install with: python3 -m pip install pyserial", file=sys.stderr)
        print(f"Import error: {e}", file=sys.stderr)
        return 2

    try:
        import cv2  # noqa: F401
    except ImportError as e:
        print("Missing dependency: opencv-python", file=sys.stderr)
        print("Install with: python3 -m pip install opencv-python", file=sys.stderr)
        print(f"Import error: {e}", file=sys.stderr)
        return 2

    if args.display:
        init_opencv_window(DISPLAY_WINDOW_NAME)
        print(
            f"Display: OpenCV window '{DISPLAY_WINDOW_NAME}' (press Q in window to quit).",
            flush=True,
        )

    save_dir = Path(args.save_dir).expanduser().resolve()
    save_dir.mkdir(parents=True, exist_ok=True)

    min_save_period = 1.0 / float(args.save_fps) if args.save_fps > 0 else 0.0
    last_save_ts = 0.0
    last_chime_ts = 0.0
    invoke_count = 0
    invoke_with_image = 0
    bytes_received = 0
    json_objects = 0
    dropped_invoke_messages = 0
    last_status_ts = time.time()
    last_display_ts = 0.0
    display_period = 1.0 / float(args.display_fps) if args.display and args.display_fps > 0 else 0.0
    serial_stall_seconds = max(1.0, float(args.stall_reconnect_seconds))
    open_grace_seconds = max(0.0, float(args.open_grace_seconds))
    last_serial_byte_ts = time.time()
    open_grace_until = 0.0

    latest_jpg: Optional[bytes] = None
    latest_boxes: List[DetectionBox] = []
    latest_decoded_frame: Optional[Any] = None
    latest_decoded_jpg_id: Optional[int] = None
    frame_lock = threading.Lock()

    buffer = bytearray()
    buffer_lock = threading.Lock()
    serial_stop = threading.Event()
    serial_disconnect = threading.Event()
    serial_disconnect_reason: List[str] = [""]
    recovery_requested = threading.Event()

    ser: Any = None
    serial_io_lock = threading.Lock()
    reconnect_delay = max(0.0, float(args.reconnect_delay))
    reconnect_log_interval = max(0.0, float(args.reconnect_log_interval))
    last_reconnect_log_ts = -1e9
    hinted_missing_port = False

    def note_serial_bytes(count: int) -> None:
        nonlocal bytes_received, last_serial_byte_ts
        if count <= 0:
            return
        bytes_received += count
        last_serial_byte_ts = time.time()

    def append_serial_chunk(chunk: bytes) -> None:
        nonlocal dropped_invoke_messages
        note_serial_bytes(len(chunk))
        with buffer_lock:
            buffer.extend(chunk)
            if trim_oversized_serial_buffer(buffer, MAX_SERIAL_BUFFER_BYTES):
                print(
                    "GV2 serial: buffer overflow while waiting for complete JSON; "
                    "discarded partial data.",
                    file=sys.stderr,
                    flush=True,
                )
            if drop_stale_invoke_messages(buffer):
                dropped_invoke_messages += 1

    def reconnect_warn(message: str) -> None:
        nonlocal last_reconnect_log_ts
        now_ts = time.time()
        if reconnect_log_interval <= 0 or (now_ts - last_reconnect_log_ts) >= reconnect_log_interval:
            print(message, file=sys.stderr, flush=True)
            last_reconnect_log_ts = now_ts

    def open_serial_port() -> Any:
        ser_obj = serial.Serial(args.port, args.baudrate, timeout=args.serial_timeout)
        ser_obj.reset_input_buffer()
        ser_obj.dtr = True
        ser_obj.rts = True
        return ser_obj

    def serial_reader_loop() -> None:
        while not serial_stop.is_set():
            with serial_io_lock:
                current = ser
            if current is None:
                time.sleep(0.01)
                continue
            try:
                drained_any = False
                while True:
                    waiting = current.in_waiting
                    if waiting > 0:
                        read_size = min(waiting, MAX_SERIAL_READ_BYTES)
                        chunk = current.read(read_size)
                    else:
                        if drained_any:
                            break
                        chunk = current.read(1)
                    if not chunk:
                        break
                    drained_any = True
                    append_serial_chunk(chunk)
            except (serial.SerialException, OSError) as exc:
                with serial_io_lock:
                    if ser is not current:
                        time.sleep(0.02)
                        continue
                serial_disconnect_reason[0] = str(exc)
                serial_disconnect.set()
                time.sleep(0.05)
            except Exception as exc:
                serial_disconnect_reason[0] = str(exc)
                serial_disconnect.set()
                time.sleep(0.05)

    def processor_loop() -> None:
        nonlocal invoke_count, invoke_with_image, json_objects, dropped_invoke_messages
        nonlocal latest_jpg, latest_boxes, last_save_ts, last_chime_ts

        while not serial_stop.is_set():
            with buffer_lock:
                objects, remainder = extract_complete_json_objects(buffer)
                buffer[:] = remainder

            if not objects:
                time.sleep(0.001)
                continue

            if len(objects) > 1:
                skipped = len(objects) - 1
                dropped_invoke_messages += skipped
                json_objects += skipped
                objects = [objects[-1]]

            obj_bytes = objects[0]
            json_objects += 1
            try:
                obj = json.loads(obj_bytes.decode("utf-8", errors="ignore"))
            except json.JSONDecodeError:
                if args.verbose:
                    print(f"JSON decode failed ({len(obj_bytes)} bytes)", flush=True)
                continue

            if not isinstance(obj, dict) or obj.get("name") != "INVOKE":
                if args.verbose and isinstance(obj, dict) and obj.get("name"):
                    print(f"serial message: {obj.get('name')}", flush=True)
                continue

            invoke_count += 1
            detection_boxes = parse_detection_boxes(obj)
            class_id, score = parse_best_box(obj)
            jpg = decode_jpeg_from_invoke(obj)

            if jpg:
                invoke_with_image += 1
                with frame_lock:
                    latest_jpg = jpg
                    latest_boxes = detection_boxes
            elif args.verbose:
                print("INVOKE without decodable image field", flush=True)

            if score is None:
                continue

            now = time.time()
            if score >= float(args.chime_threshold) and (now - last_chime_ts) >= float(
                args.chime_cooldown_seconds
            ):
                last_chime_ts = now
                threading.Thread(target=play_chime, args=(args.sound,), daemon=True).start()

            if score < float(args.save_threshold):
                continue
            if min_save_period > 0 and (now - last_save_ts) < min_save_period:
                continue
            if not jpg:
                continue

            last_save_ts = now
            ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            cname = safe_class_name(class_id)
            stem = f"{ts}_{cname}_{score:.3f}"
            out = save_dir / f"{stem}.jpg"
            out.write_bytes(jpg)
            boxed_out = save_dir / f"{stem}_boxed.jpg"
            if not save_jpeg_with_boxes(jpg, detection_boxes, boxed_out):
                print(
                    f"GV2 save: failed to write annotated image {boxed_out.name}",
                    file=sys.stderr,
                    flush=True,
                )

    def start_worker(name: str, target: Any) -> threading.Thread:
        thread = threading.Thread(target=target, name=name, daemon=True)
        thread.start()
        return thread

    reader_thread = start_worker("gv2-serial-reader", serial_reader_loop)
    processor_thread = start_worker("gv2-processor", processor_loop)

    def ensure_worker_threads() -> None:
        nonlocal reader_thread, processor_thread
        if not reader_thread.is_alive():
            print("GV2 serial: restarting reader thread...", file=sys.stderr, flush=True)
            reader_thread = start_worker("gv2-serial-reader", serial_reader_loop)
        if not processor_thread.is_alive():
            print("GV2 serial: restarting processor thread...", file=sys.stderr, flush=True)
            processor_thread = start_worker("gv2-processor", processor_loop)

    def close_serial_port() -> None:
        nonlocal ser
        with serial_io_lock:
            old_ser = ser
            ser = None
        _safe_close_serial(old_ser)
        time.sleep(0.05)

    def recover_serial(reason: str, *, usb_reset: bool) -> None:
        nonlocal open_grace_until
        reconnect_warn(reason)
        close_serial_port()
        with buffer_lock:
            buffer.clear()
        if usb_reset and not args.no_usb_reset:
            reconnect_warn("GV2 serial: pulsing USB reset (DTR/RTS)...")
            pulse_usb_reset(args.port, args.baudrate, boot_seconds=USB_RESET_BOOT_SECONDS)
        elif reconnect_delay:
            time.sleep(reconnect_delay)
        open_grace_until = time.time() + open_grace_seconds
        recovery_requested.set()

    def maybe_print_status(force: bool = False) -> None:
        nonlocal last_status_ts
        if args.status_interval <= 0:
            return
        now = time.time()
        if not force and (now - last_status_ts) < args.status_interval:
            return
        last_status_ts = now
        with buffer_lock:
            buffer_len = len(buffer)
        with frame_lock:
            has_frame = latest_jpg is not None
        idle_s = now - last_serial_byte_ts
        print(
            f"GV2 status: bytes={bytes_received} json={json_objects} "
            f"invoke={invoke_count} with_image={invoke_with_image} "
            f"buffer={buffer_len} dropped={dropped_invoke_messages} "
            f"idle={idle_s:.1f}s reader={'alive' if reader_thread.is_alive() else 'dead'} "
            f"proc={'alive' if processor_thread.is_alive() else 'dead'} "
            f"displayed={'yes' if has_frame else 'no'}",
            file=sys.stderr,
            flush=True,
        )

    def get_decoded_display_frame() -> Any:
        nonlocal latest_decoded_frame, latest_decoded_jpg_id
        with frame_lock:
            jpg = latest_jpg
            boxes = list(latest_boxes)

        if jpg:
            jpg_id = id(jpg)
            if latest_decoded_frame is None or latest_decoded_jpg_id != jpg_id:
                latest_decoded_frame = decode_jpeg_image(jpg)
                latest_decoded_jpg_id = jpg_id
            if latest_decoded_frame is not None:
                visible_boxes = [box for box in boxes if box.score >= float(args.display_min_score)]
                return draw_detection_boxes(latest_decoded_frame, visible_boxes)
            return make_status_frame(["GV2 detections", "JPEG decode failed"])
        return make_status_frame(["GV2 detections", "Waiting for INVOKE..."])

    def refresh_display_if_due(*, force: bool = False) -> bool:
        nonlocal last_display_ts
        if not args.display:
            return False
        now = time.time()
        if not force and display_period > 0 and (now - last_display_ts) < display_period:
            return False
        last_display_ts = now
        import cv2

        cv2.imshow(DISPLAY_WINDOW_NAME, get_decoded_display_frame())
        key = cv2.waitKey(1) & 0xFF
        return key in (ord("q"), ord("Q"))

    try:
        while True:
            ensure_worker_threads()

            if recovery_requested.is_set() or ser is None:
                recovery_requested.clear()
                try:
                    with serial_io_lock:
                        ser = open_serial_port()
                except (serial.SerialException, OSError) as e:
                    if not _is_serial_disconnect(e, serial):
                        raise
                    reconnect_warn(f"GV2 serial: open failed ({e}), retrying...")
                    if not hinted_missing_port and _chain_has_errno(e, errno.ENOENT):
                        hinted_missing_port = True
                        print(
                            "GV2 serial: no device node yet (ENOENT). Plug in GV2/USB, "
                            "then check: ls /dev/cu.*usb*",
                            file=sys.stderr,
                            flush=True,
                        )
                    close_serial_port()
                    if reconnect_delay:
                        time.sleep(reconnect_delay)
                    if refresh_display_if_due(force=True):
                        return 0
                    maybe_print_status()
                    continue

                last_reconnect_log_ts = float("-inf")
                open_grace_until = time.time() + open_grace_seconds
                serial_disconnect.clear()
                print(f"GV2 serial: opened {args.port}", file=sys.stderr, flush=True)

            if serial_disconnect.is_set():
                reason = serial_disconnect_reason[0] or "serial read failed"
                serial_disconnect.clear()
                recover_serial(f"GV2 serial disconnected ({reason}), reconnecting...", usb_reset=False)
                if refresh_display_if_due(force=True):
                    return 0
                maybe_print_status()
                continue

            now = time.time()
            if (
                ser is not None
                and now >= open_grace_until
                and (now - last_serial_byte_ts) >= serial_stall_seconds
            ):
                recover_serial(
                    f"GV2 serial: no bytes for {serial_stall_seconds:.1f}s "
                    "(device UART blocked); recovering with USB reset...",
                    usb_reset=True,
                )
                if refresh_display_if_due(force=True):
                    return 0
                maybe_print_status()
                continue

            if refresh_display_if_due():
                return 0
            maybe_print_status()
            time.sleep(0.001)

    except KeyboardInterrupt:
        return 0
    finally:
        serial_stop.set()
        reader_thread.join(timeout=1.0)
        processor_thread.join(timeout=1.0)
        close_serial_port()
        if args.display:
            try:
                import cv2

                cv2.destroyAllWindows()
            except Exception:
                pass
        if args.verbose:
            print(
                f"INVOKE stats: total={invoke_count} with_image={invoke_with_image}",
                flush=True,
            )


if __name__ == "__main__":
    raise SystemExit(main())
