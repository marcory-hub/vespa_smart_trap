#!/usr/bin/env python3
"""
Run a fixed 5-model GV2 experiment session and aggregate per-run summaries.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable, Optional


EXACT_MATCH_RE = re.compile(
    r"Overall exact set match rate:\s*([0-9]*\.?[0-9]+)\s*\((\d+)\s*/\s*(\d+)\)"
)


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def list_output_run_dirs(outputs_root: Path) -> set[str]:
    if not outputs_root.exists():
        return set()
    return {p.name for p in outputs_root.iterdir() if p.is_dir()}


def prompt_operator_for_model(model_name: str, index: int, total: int) -> str:
    print()
    print(f"[{index}/{total}] Next model: {model_name}")
    print("Flash/swap this model on the GV2 device, then press Enter to continue.")
    print("Type 'skip' to skip this model, or 'quit' to stop the session.")
    reply = input("> ").strip().lower()
    if reply == "quit":
        return "quit"
    if reply == "skip":
        return "skip"
    return "run"


def parse_exact_rate(stdout_text: str) -> tuple[Optional[float], Optional[int], Optional[int]]:
    match = EXACT_MATCH_RE.search(stdout_text)
    if not match:
        return None, None, None
    rate = float(match.group(1))
    numerator = int(match.group(2))
    denominator = int(match.group(3))
    return rate, numerator, denominator


def build_run_command(
    run_script: Path,
    model_name: str,
    slider_port: int,
    expected_count: int,
    serial_port: Optional[str],
    serial_port_glob: Optional[str],
    serial_baudrate: int,
    serial_read_timeout: float,
    slider_wait_runlog_seconds: float,
    skip_open_browser: bool,
    locked_benchmark: bool,
) -> list[str]:
    command = [
        sys.executable,
        str(run_script),
        "--model-name",
        model_name,
        "--slider-port",
        str(slider_port),
        "--expected-count",
        str(expected_count),
        "--serial-baudrate",
        str(serial_baudrate),
        "--serial-read-timeout",
        str(serial_read_timeout),
        "--slider-wait-runlog-seconds",
        str(slider_wait_runlog_seconds),
    ]
    if serial_port:
        command.extend(["--serial-port", serial_port])
    elif serial_port_glob:
        command.extend(["--serial-port-glob", serial_port_glob])
    if skip_open_browser:
        command.append("--skip-open-browser")
    if locked_benchmark:
        command.append("--locked-benchmark")
    return command


def run_with_live_output(command: list[str], working_directory: Path) -> tuple[int, str]:
    process = subprocess.Popen(
        command,
        cwd=str(working_directory),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    captured_lines: list[str] = []
    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="")
        captured_lines.append(line)
    return_code = process.wait()
    return return_code, "".join(captured_lines)


def write_aggregate_csv(path: Path, rows: Iterable[dict[str, str]]) -> None:
    fieldnames = [
        "run_index",
        "model_name",
        "status",
        "started_at_iso",
        "ended_at_iso",
        "duration_s",
        "run_output_dir",
        "exact_set_match_rate",
        "exact_match_numerator",
        "exact_match_denominator",
        "command",
    ]
    with path.open("w", newline="", encoding="utf-8") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def run() -> None:
    parser = argparse.ArgumentParser(description="Run and aggregate a fixed 5-model GV2 session.")
    parser.add_argument(
        "--model-name",
        action="append",
        dest="model_names",
        required=True,
        help="Model name in fixed execution order. Repeat exactly five times.",
    )
    parser.add_argument("--serial-port", default=None, help="Explicit serial port path.")
    parser.add_argument(
        "--serial-port-glob",
        default="/dev/tty.usbmodem*",
        help="Serial port glob fallback (used only when --serial-port is absent).",
    )
    parser.add_argument("--slider-port", type=int, default=8000, help="Slider server port.")
    parser.add_argument("--expected-count", type=int, default=388, help="Expected image count per run.")
    parser.add_argument("--serial-baudrate", type=int, default=921600, help="Serial baudrate.")
    parser.add_argument("--serial-read-timeout", type=float, default=0.2, help="Serial read timeout.")
    parser.add_argument(
        "--slider-wait-runlog-seconds",
        type=float,
        default=300.0,
        help="Wait for slider run_log.csv.",
    )
    parser.add_argument("--skip-open-browser", action="store_true", help="Do not open browser window.")
    parser.add_argument(
        "--locked-benchmark",
        action="store_true",
        help="Run experiment in strict locked benchmark mode.",
    )
    args = parser.parse_args()

    model_names = args.model_names or []
    if len(model_names) != 5:
        raise ValueError(f"Expected exactly 5 --model-name values, got {len(model_names)}.")

    repo_root = Path(__file__).resolve().parents[2]
    outputs_root = repo_root / "outputs"
    outputs_root.mkdir(parents=True, exist_ok=True)
    run_script = Path(__file__).resolve().parent / "run_experiment.py"

    session_timestamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    session_dir = outputs_root / f"{session_timestamp}__five_model_session"
    session_dir.mkdir(parents=False, exist_ok=False)
    aggregate_csv_path = session_dir / "aggregate_summary.csv"

    aggregate_rows: list[dict[str, str]] = []
    total = len(model_names)

    for index, model_name in enumerate(model_names, start=1):
        operator_action = prompt_operator_for_model(model_name=model_name, index=index, total=total)
        if operator_action == "quit":
            print("Session stopped by operator request.")
            break
        if operator_action == "skip":
            aggregate_rows.append(
                {
                    "run_index": str(index),
                    "model_name": model_name,
                    "status": "skipped_by_operator",
                    "started_at_iso": "",
                    "ended_at_iso": "",
                    "duration_s": "",
                    "run_output_dir": "",
                    "exact_set_match_rate": "",
                    "exact_match_numerator": "",
                    "exact_match_denominator": "",
                    "command": "",
                }
            )
            continue

        # Skip marker support.
        if sys.stdin is not None and sys.stdin.closed:
            raise RuntimeError("stdin is unavailable for operator checkpoint input.")

        started_at = now_iso()
        started_epoch = time.time()
        before_dirs = list_output_run_dirs(outputs_root)

        command = build_run_command(
            run_script=run_script,
            model_name=model_name,
            slider_port=args.slider_port,
            expected_count=args.expected_count,
            serial_port=args.serial_port,
            serial_port_glob=args.serial_port_glob,
            serial_baudrate=args.serial_baudrate,
            serial_read_timeout=args.serial_read_timeout,
            slider_wait_runlog_seconds=args.slider_wait_runlog_seconds,
            skip_open_browser=args.skip_open_browser,
            locked_benchmark=args.locked_benchmark,
        )
        print(f"Running: {' '.join(command)}")
        return_code, combined_output = run_with_live_output(command=command, working_directory=repo_root)

        ended_at = now_iso()
        duration_s = f"{(time.time() - started_epoch):.3f}"

        after_dirs = list_output_run_dirs(outputs_root)
        new_dirs = sorted(after_dirs - before_dirs)
        run_output_dir = ""
        if new_dirs:
            run_output_dir = str((outputs_root / new_dirs[-1]).relative_to(repo_root))

        rate, numerator, denominator = parse_exact_rate(combined_output)
        status = "ok" if return_code == 0 else f"failed_exit_{return_code}"
        aggregate_rows.append(
            {
                "run_index": str(index),
                "model_name": model_name,
                "status": status,
                "started_at_iso": started_at,
                "ended_at_iso": ended_at,
                "duration_s": duration_s,
                "run_output_dir": run_output_dir,
                "exact_set_match_rate": "" if rate is None else f"{rate:.6f}",
                "exact_match_numerator": "" if numerator is None else str(numerator),
                "exact_match_denominator": "" if denominator is None else str(denominator),
                "command": " ".join(command),
            }
        )

    write_aggregate_csv(path=aggregate_csv_path, rows=aggregate_rows)
    print(f"Aggregate summary written to: {aggregate_csv_path}")


if __name__ == "__main__":
    run()

