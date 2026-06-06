#!/usr/bin/env python3
"""
Set YOLO class id (first whitespace-separated token) per filename prefix:
  top_*.txt -> class 0 on every non-empty line
  oth_*.txt -> class 1 on every non-empty line

Files whose names contain NULL (e.g. top_NULL_..., oth_NULL_...) are skipped entirely
so they remain empty.

Dry-run by default; use --apply to write files. Back up labels/ before --apply.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TOP_PREFIX = "top_"
OTH_PREFIX = "oth_"


def _is_null_label(path: Path) -> bool:
    return "NULL" in path.name.upper()


def _is_top_or_oth_label(path: Path) -> bool:
    name = path.name.lower()
    return name.startswith(TOP_PREFIX) or name.startswith(OTH_PREFIX)


def _class_token_for_path(path: Path) -> str:
    """Return YOLO class token for this label file (top_ -> 0, oth_ -> 1)."""
    name = path.name.lower()
    if name.startswith(TOP_PREFIX):
        return "0"
    if name.startswith(OTH_PREFIX):
        return "1"
    raise ValueError(f"Expected top_ or oth_ prefix: {path.name}")


def rewrite_yolo_lines(text: str, class_token: str) -> tuple[str, int]:
    """
    For each non-blank line, set the first field to class_token. Blank lines are kept.
    Returns (new_text, number_of_lines_changed).
    """
    changed = 0
    out_parts: list[str] = []
    lines = text.splitlines(keepends=True)
    if not lines and text == "":
        return "", 0

    for line in lines:
        if not line.strip():
            out_parts.append(line)
            continue
        newline = ""
        body = line
        if body.endswith("\r\n"):
            newline = "\r\n"
            body = body[:-2]
        elif body.endswith("\n"):
            newline = "\n"
            body = body[:-1]
        elif body.endswith("\r"):
            newline = "\r"
            body = body[:-1]

        parts = body.split(maxsplit=1)
        if len(parts) == 1:
            new_body = class_token
        else:
            new_body = class_token + " " + parts[1]

        if new_body != body:
            changed += 1
        out_parts.append(new_body + newline)

    return "".join(out_parts), changed


def process_file(path: Path, apply: bool) -> tuple[bool, int, str | None]:
    """
    Returns (would_modify, lines_changed, error_message).
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return False, 0, str(exc)

    class_token = _class_token_for_path(path)
    new_text, lines_changed = rewrite_yolo_lines(text, class_token)
    if new_text == text:
        return False, 0, None
    if apply:
        try:
            path.write_text(new_text, encoding="utf-8")
        except OSError as exc:
            return True, lines_changed, str(exc)
    return True, lines_changed, None


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Set first YOLO class token: 0 for top_*.txt, 1 for oth_*.txt label files."
        )
    )
    parser.add_argument(
        "--labels-dir",
        type=Path,
        required=True,
        help="Directory containing YOLO .txt label files (e.g. data/dataset/labels).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write changes (default is dry-run only).",
    )
    args = parser.parse_args()

    labels_dir = args.labels_dir.expanduser().resolve()
    if not labels_dir.is_dir():
        print(f"ERROR: not a directory: {labels_dir}", file=sys.stderr)
        return 2

    candidates = sorted(
        p for p in labels_dir.iterdir()
        if p.is_file() and p.suffix.lower() == ".txt"
    )

    to_process = [p for p in candidates if _is_top_or_oth_label(p) and not _is_null_label(p)]
    skipped_null = [p for p in candidates if _is_top_or_oth_label(p) and _is_null_label(p)]
    skipped_other = [p for p in candidates if not _is_top_or_oth_label(p)]

    n_top = sum(1 for p in to_process if p.name.lower().startswith(TOP_PREFIX))
    n_oth = sum(1 for p in to_process if p.name.lower().startswith(OTH_PREFIX))

    print(f"Labels directory: {labels_dir}")
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")
    print(
        f"top_/oth_ label files to scan (excluding NULL): {len(to_process)} "
        f"(top_->0: {n_top}, oth_->1: {n_oth})"
    )
    print(f"Skipped top_/oth_*NULL* (left unchanged): {len(skipped_null)}")
    print(f"Skipped other .txt: {len(skipped_other)}")
    print()

    total_changes = 0
    modified_files = 0
    errors: list[str] = []

    for path in to_process:
        class_token = _class_token_for_path(path)
        would_modify, lines_changed, err = process_file(path, apply=args.apply)
        if err:
            errors.append(f"{path.name}: {err}")
            continue
        if not would_modify:
            continue
        modified_files += 1
        total_changes += lines_changed
        print(
            f"  {path.name}: {lines_changed} line(s) -> class token set to {class_token}"
        )

    print()
    if modified_files == 0:
        print("No files needed updates (already match top_=0 / oth_=1 or empty).")
    else:
        print(
            f"Summary: {modified_files} file(s), {total_changes} line(s) "
            f"with class token updated."
        )
        if not args.apply:
            print("Re-run with --apply to write these changes.")

    if errors:
        print("ERRORS:", file=sys.stderr)
        for line in errors:
            print(line, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
