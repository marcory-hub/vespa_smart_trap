#!/usr/bin/env python3
"""
Manually verify top vs other folder placement in data/dataset_top.

Reviews every image in the six *_top / *_oth / val_other folders (NULL folders skipped).
Press T/O to reclassify and move mis-filed pairs; N or Space when placement is correct.
State is persisted so sessions can resume without duplicate review.

Example:
  source .venv/bin/activate
  python scripts/dataset_top_select/review_folder_placement.py \\
    --dataset-root data/dataset_top
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
SOURCE_SPLITS = ("train", "val", "test")
VIEW_TOP = "top"
VIEW_OTHER = "other"

TOP_FOLDER_BY_SPLIT = {
    "train": "train_top",
    "val": "val_top",
    "test": "test_top",
}
OTHER_FOLDER_BY_SPLIT = {
    "train": "train_oth",
    "val": "val_other",
    "test": "test_oth",
}
REVIEW_IMAGE_FOLDERS = tuple(
    TOP_FOLDER_BY_SPLIT[split] for split in SOURCE_SPLITS
) + tuple(OTHER_FOLDER_BY_SPLIT[split] for split in SOURCE_SPLITS)

FOLDER_TO_SPLIT_VIEW: dict[str, tuple[str, str]] = {}
for split in SOURCE_SPLITS:
    FOLDER_TO_SPLIT_VIEW[TOP_FOLDER_BY_SPLIT[split]] = (split, VIEW_TOP)
    FOLDER_TO_SPLIT_VIEW[OTHER_FOLDER_BY_SPLIT[split]] = (split, VIEW_OTHER)

STATE_VERSION = 1
DEFAULT_STATE_NAME = ".review_folder_placement.json"
DEFAULT_MOVES_LOG_NAME = "review_moves.log"
IMAGES_ACTIVE_DIR = "images"
LABELS_ACTIVE_DIR = "labels"
IMAGES_REVIEWED_DIR = "images_reviewed"
LABELS_REVIEWED_DIR = "labels_reviewed"
ARCHIVE_LOG_NAME = "archive_reviewed.log"
WINDOW_NAME = "folder placement review"
MAX_DISPLAY_WIDTH = 1280
FOOTER_HEIGHT = 40
FOOTER_BG_COLOR = (40, 40, 40)


@dataclass(frozen=True)
class QueueItem:
    split: str
    stem: str
    image_path: Path
    label_path: Path
    current_folder: str
    current_view: str

    @property
    def reviewed_key(self) -> tuple[str, str]:
        return (self.split, self.stem)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Review top vs other folder placement in dataset_top (OpenCV UI).",
    )
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=Path("data/dataset_top"),
        help="Root with images/ and labels/ subfolders (default: data/dataset_top).",
    )
    parser.add_argument(
        "--state-file",
        type=Path,
        default=None,
        help=f"Resume state JSON (default: <dataset-root>/{DEFAULT_STATE_NAME}).",
    )
    parser.add_argument(
        "--moves-log",
        type=Path,
        default=None,
        help=f"Move audit log (default: <dataset-root>/{DEFAULT_MOVES_LOG_NAME}).",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear saved review state before starting.",
    )
    parser.add_argument(
        "--splits",
        nargs="+",
        choices=list(SOURCE_SPLITS),
        default=list(SOURCE_SPLITS),
        help="Limit review to specific splits (default: train val test).",
    )
    parser.add_argument(
        "--start-at",
        type=int,
        metavar="N",
        default=None,
        help=(
            "Start at image N in the full sorted queue (1-based). "
            "Marks images 1..N-1 as reviewed and saves state before opening the UI."
        ),
    )
    parser.add_argument(
        "--restore-unreviewed",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Before opening the UI, move images from images_reviewed/ back to images/ "
            "when (split, stem) is not in saved reviewed[] state (default: on)."
        ),
    )
    parser.add_argument(
        "--restore-unreviewed-only",
        action="store_true",
        help="Run --restore-unreviewed and exit (no UI). Combine with --dry-run to preview.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="With --restore-unreviewed-only: print what would be restored without moving files.",
    )
    return parser.parse_args()


def is_null_jpg(path: Path) -> bool:
    return path.suffix.lower() == ".jpg" and "null" in path.stem.lower()


def iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def folder_for_view(split: str, view: Literal["top", "other"]) -> str:
    if view == VIEW_TOP:
        return TOP_FOLDER_BY_SPLIT[split]
    return OTHER_FOLDER_BY_SPLIT[split]




def folders_for_split(split: str) -> tuple[str, str]:
    return TOP_FOLDER_BY_SPLIT[split], OTHER_FOLDER_BY_SPLIT[split]


def resolve_queue_item(item: QueueItem, dataset_root: Path) -> QueueItem | None:
    """Locate image/label in active images/ folders (paths in queue may be stale)."""
    return locate_active_item(dataset_root, item.split, item.stem)




def locate_active_item(dataset_root: Path, split: str, stem: str) -> QueueItem | None:
    """Find image/label under images/ and labels/ only."""
    images_root = dataset_root / IMAGES_ACTIVE_DIR
    labels_root = dataset_root / LABELS_ACTIVE_DIR
    for folder_name in folders_for_split(split):
        for suffix in IMAGE_SUFFIXES:
            image_path = images_root / folder_name / f"{stem}{suffix}"
            if not image_path.is_file():
                continue
            _split, view = FOLDER_TO_SPLIT_VIEW[folder_name]
            label_path = labels_root / folder_name / f"{stem}.txt"
            return QueueItem(
                split=split,
                stem=stem,
                image_path=image_path,
                label_path=label_path,
                current_folder=folder_name,
                current_view=view,
            )
    return None


def locate_reviewed_item(dataset_root: Path, split: str, stem: str) -> QueueItem | None:
    """Find image/label under images_reviewed/ and labels_reviewed/."""
    images_root = dataset_root / IMAGES_REVIEWED_DIR
    labels_root = dataset_root / LABELS_REVIEWED_DIR
    for folder_name in folders_for_split(split):
        for suffix in IMAGE_SUFFIXES:
            image_path = images_root / folder_name / f"{stem}{suffix}"
            if not image_path.is_file():
                continue
            _split, view = FOLDER_TO_SPLIT_VIEW[folder_name]
            label_path = labels_root / folder_name / f"{stem}.txt"
            return QueueItem(
                split=split,
                stem=stem,
                image_path=image_path,
                label_path=label_path,
                current_folder=folder_name,
                current_view=view,
            )
    return None


def archive_item_to_reviewed(
    item: QueueItem,
    dataset_root: Path,
    archive_log: Path | None = None,
    dry_run: bool = False,
) -> tuple[bool, str]:
    """Move reviewed image+label from active folders to images_reviewed/."""
    if IMAGES_REVIEWED_DIR in item.image_path.parts:
        return True, "Already archived."

    dest_image = dataset_root / IMAGES_REVIEWED_DIR / item.current_folder / item.image_path.name
    dest_label = dataset_root / LABELS_REVIEWED_DIR / item.current_folder / f"{item.stem}.txt"

    if dest_image.exists():
        return False, f"Collision: {dest_image} exists"
    if item.label_path.is_file() and dest_label.exists():
        return False, f"Collision: {dest_label} exists"

    if dry_run:
        return True, f"Would archive -> {dest_image.parent.name}/"

    dest_image.parent.mkdir(parents=True, exist_ok=True)
    dest_label.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(item.image_path), str(dest_image))
    label_moved = False
    if item.label_path.is_file():
        shutil.move(str(item.label_path), str(dest_label))
        label_moved = True

    if archive_log is not None:
        append_moves_log(
            archive_log,
            f"{iso_now()} split={item.split} stem={item.stem} "
            f"{item.current_folder} active->reviewed label_moved={label_moved}",
        )
    return True, f"Archived -> {item.current_folder}"


def restore_item_from_reviewed(
    item: QueueItem,
    dataset_root: Path,
    archive_log: Path | None = None,
    dry_run: bool = False,
) -> tuple[bool, str, QueueItem | None]:
    """Move image+label from images_reviewed/ back to active folders."""
    reviewed = locate_reviewed_item(dataset_root, item.split, item.stem)
    if reviewed is None:
        active = locate_active_item(dataset_root, item.split, item.stem)
        if active is not None:
            return True, "Already in active folders.", active
        return False, f"Not found in reviewed or active: {item.stem}", None

    dest_image = dataset_root / IMAGES_ACTIVE_DIR / reviewed.current_folder / reviewed.image_path.name
    dest_label = dataset_root / LABELS_ACTIVE_DIR / reviewed.current_folder / f"{reviewed.stem}.txt"

    if dest_image.exists():
        return False, f"Collision: {dest_image} exists", None
    if reviewed.label_path.is_file() and dest_label.exists():
        return False, f"Collision: {dest_label} exists", None

    if dry_run:
        return True, "Would restore to active.", reviewed

    dest_image.parent.mkdir(parents=True, exist_ok=True)
    dest_label.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(reviewed.image_path), str(dest_image))
    if reviewed.label_path.is_file():
        shutil.move(str(reviewed.label_path), str(dest_label))

    restored = QueueItem(
        split=reviewed.split,
        stem=reviewed.stem,
        image_path=dest_image,
        label_path=dest_label,
        current_folder=reviewed.current_folder,
        current_view=reviewed.current_view,
    )
    if archive_log is not None:
        append_moves_log(
            archive_log,
            f"{iso_now()} split={item.split} stem={item.stem} "
            f"{item.current_folder} reviewed->active label_moved=True",
        )
    return True, "Restored to active.", restored


def load_state(state_path: Path) -> dict:
    if not state_path.is_file():
        return {
            "version": STATE_VERSION,
            "dataset_root": "",
            "reviewed": [],
            "moves": [],
            "queue_order": "sorted_path",
        }
    data = json.loads(state_path.read_text(encoding="utf-8"))
    reviewed = {tuple(pair) for pair in data.get("reviewed", [])}
    data["_reviewed_set"] = reviewed
    return data


def save_state(state_path: Path, dataset_root: Path, reviewed: set[tuple[str, str]], moves: list[dict]) -> None:
    payload = {
        "version": STATE_VERSION,
        "dataset_root": str(dataset_root.resolve()),
        "reviewed": sorted(reviewed),
        "moves": moves,
        "queue_order": "sorted_path",
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def append_moves_log(log_path: Path, line: str) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(line.rstrip() + "\n")


def build_queue(dataset_root: Path, splits: list[str], reviewed: set[tuple[str, str]]) -> list[QueueItem]:
    images_root = dataset_root / IMAGES_ACTIVE_DIR
    labels_root = dataset_root / LABELS_ACTIVE_DIR
    items: list[QueueItem] = []

    for folder_name in REVIEW_IMAGE_FOLDERS:
        split, view = FOLDER_TO_SPLIT_VIEW[folder_name]
        if split not in splits:
            continue
        images_dir = images_root / folder_name
        labels_dir = labels_root / folder_name
        if not images_dir.is_dir():
            print(f"Warning: missing folder {images_dir}", file=sys.stderr)
            continue

        for image_path in sorted(images_dir.iterdir()):
            if not image_path.is_file():
                continue
            if image_path.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            if is_null_jpg(image_path):
                continue
            stem = image_path.stem
            key = (split, stem)
            if key in reviewed:
                continue
            label_path = labels_dir / f"{stem}.txt"
            items.append(
                QueueItem(
                    split=split,
                    stem=stem,
                    image_path=image_path,
                    label_path=label_path,
                    current_folder=folder_name,
                    current_view=view,
                )
            )

    items.sort(key=lambda item: (item.split, item.current_folder, item.image_path.name))
    return items


def iter_archived_items(dataset_root: Path, splits: list[str]) -> list[QueueItem]:
    """List every non-NULL image currently under images_reviewed/ (six view folders)."""
    images_root = dataset_root / IMAGES_REVIEWED_DIR
    labels_root = dataset_root / LABELS_REVIEWED_DIR
    items: list[QueueItem] = []

    for folder_name in REVIEW_IMAGE_FOLDERS:
        split, view = FOLDER_TO_SPLIT_VIEW[folder_name]
        if split not in splits:
            continue
        images_dir = images_root / folder_name
        labels_dir = labels_root / folder_name
        if not images_dir.is_dir():
            continue

        for image_path in sorted(images_dir.iterdir()):
            if not image_path.is_file():
                continue
            if image_path.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            if is_null_jpg(image_path):
                continue
            stem = image_path.stem
            label_path = labels_dir / f"{stem}.txt"
            items.append(
                QueueItem(
                    split=split,
                    stem=stem,
                    image_path=image_path,
                    label_path=label_path,
                    current_folder=folder_name,
                    current_view=view,
                )
            )

    items.sort(key=lambda item: (item.split, item.current_folder, item.image_path.name))
    return items


@dataclass
class RestoreSummary:
    restored: int = 0
    already_active: int = 0
    skipped_reviewed: int = 0
    failed: int = 0
    errors: list[str] | None = None

    def __post_init__(self) -> None:
        if self.errors is None:
            self.errors = []


def restore_unreviewed_archived(
    dataset_root: Path,
    splits: list[str],
    reviewed: set[tuple[str, str]],
    archive_log: Path | None = None,
    dry_run: bool = False,
) -> RestoreSummary:
    """
    Move archived pairs back to active folders when not in reviewed[].

    Lets you resume manual review after bulk archive (sequence fill) without
    touching stems already marked reviewed in state.
    """
    summary = RestoreSummary()
    for item in iter_archived_items(dataset_root, splits):
        if item.reviewed_key in reviewed:
            summary.skipped_reviewed += 1
            continue

        ok, message, _restored = restore_item_from_reviewed(
            item,
            dataset_root,
            archive_log=archive_log,
            dry_run=dry_run,
        )
        if not ok:
            summary.failed += 1
            summary.errors.append(f"{item.split}/{item.stem}: {message}")
        elif message == "Already in active folders.":
            summary.already_active += 1
        else:
            summary.restored += 1

    return summary


def print_restore_summary(summary: RestoreSummary, *, dry_run: bool) -> None:
    action = "Would restore" if dry_run else "Restored"
    print(
        f"{action} {summary.restored} unreviewed image(s) from {IMAGES_REVIEWED_DIR}/ "
        f"to {IMAGES_ACTIVE_DIR}/ "
        f"(skipped reviewed: {summary.skipped_reviewed}, "
        f"already active: {summary.already_active}, failed: {summary.failed})"
    )
    if summary.errors:
        print("Restore errors:", file=sys.stderr)
        for line in summary.errors[:20]:
            print(f"  {line}", file=sys.stderr)
        if len(summary.errors) > 20:
            print(f"  ... and {len(summary.errors) - 20} more", file=sys.stderr)


def apply_start_at(
    dataset_root: Path,
    splits: list[str],
    start_at: int,
    reviewed: set[tuple[str, str]],
) -> tuple[int, QueueItem | None]:
    """
    Mark queue positions 1..start_at-1 as reviewed (full sorted queue, 1-based N).
    Returns (newly_marked_count, item_at_start_at or None).
    """
    if start_at < 1:
        raise SystemExit("--start-at must be >= 1")

    full_queue = build_queue(dataset_root, splits, set())
    if not full_queue:
        raise SystemExit("Queue is empty; nothing to start.")

    if start_at > len(full_queue):
        raise SystemExit(
            f"--start-at {start_at} is out of range; full queue has {len(full_queue)} images."
        )

    before = len(reviewed)
    for item in full_queue[: start_at - 1]:
        reviewed.add(item.reviewed_key)
    newly_marked = len(reviewed) - before
    return newly_marked, full_queue[start_at - 1]


def resize_for_display(image, max_width: int = MAX_DISPLAY_WIDTH):
    import cv2

    height, width = image.shape[:2]
    if width <= max_width:
        return image
    scale = max_width / width
    new_size = (max_width, int(height * scale))
    return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)


def compose_display_with_footer(image, status_line: str) -> tuple[object, int]:
    """Image with one status line in a footer bar below (no overlay on image)."""
    import cv2
    import numpy as np

    height, width = image.shape[:2]
    canvas = np.zeros((height + FOOTER_HEIGHT, width, 3), dtype=np.uint8)
    canvas[:height] = image
    canvas[height:] = FOOTER_BG_COLOR

    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.5
    thickness = 1
    max_text_width = width - 20
    text_size, _ = cv2.getTextSize(status_line, font, scale, thickness)
    while text_size[0] > max_text_width and scale > 0.35:
        scale -= 0.05
        text_size, _ = cv2.getTextSize(status_line, font, scale, thickness)

    text_x = 10
    text_y = height + (FOOTER_HEIGHT + text_size[1]) // 2
    cv2.putText(
        canvas,
        status_line,
        (text_x, text_y),
        font,
        scale,
        (255, 255, 255),
        thickness,
        cv2.LINE_AA,
    )
    return canvas, height


def try_move_item(
    item: QueueItem,
    dataset_root: Path,
    target_view: str,
    moves_log: Path,
) -> tuple[bool, str, str | None]:
    """Move image (+ label if present) to target_view folder. Returns (ok, message, new_folder)."""
    target_folder = folder_for_view(item.split, target_view)  # type: ignore[arg-type]

    dest_image = dataset_root / IMAGES_ACTIVE_DIR / target_folder / item.image_path.name
    dest_label = dataset_root / LABELS_ACTIVE_DIR / target_folder / f"{item.stem}.txt"

    if dest_image.exists():
        return False, f"Collision: destination exists {dest_image}", None
    if item.label_path.is_file() and dest_label.exists():
        return False, f"Collision: destination exists {dest_label}", None

    dest_image.parent.mkdir(parents=True, exist_ok=True)
    dest_label.parent.mkdir(parents=True, exist_ok=True)

    shutil.move(str(item.image_path), str(dest_image))
    label_moved = False
    if item.label_path.is_file():
        shutil.move(str(item.label_path), str(dest_label))
        label_moved = True

    log_line = (
        f"{iso_now()} split={item.split} stem={item.stem} "
        f"{item.current_folder} -> {target_folder} label_moved={label_moved}"
    )
    append_moves_log(moves_log, log_line)
    return True, f"Moved -> {target_folder}", target_folder



def read_key() -> int:
    """Read a key from the OpenCV window; waitKeyEx helps on macOS."""
    import sys

    import cv2

    if sys.platform == "darwin":
        key = cv2.waitKeyEx(0)
    else:
        key = cv2.waitKey(0)
    if key < 0:
        return -1
    return key & 0xFF


class ReviewSession:
    def __init__(
        self,
        dataset_root: Path,
        queue: list[QueueItem],
        state_path: Path,
        moves_log: Path,
        archive_log: Path,
        reviewed: set[tuple[str, str]],
        moves: list[dict],
    ) -> None:
        self.dataset_root = dataset_root
        self.queue = queue
        self.state_path = state_path
        self.moves_log = moves_log
        self.archive_log = archive_log
        self.reviewed = reviewed
        self.moves = moves
        self.index = 0
        self.status_message = ""
        self.image_display_height = 0

    @property
    def total(self) -> int:
        return len(self.queue)

    @property
    def current(self) -> QueueItem | None:
        if self.index >= len(self.queue):
            return None
        return self.queue[self.index]

    def persist(self) -> None:
        save_state(self.state_path, self.dataset_root, self.reviewed, self.moves)

    def mark_reviewed(self, item: QueueItem) -> None:
        resolved = locate_active_item(self.dataset_root, item.split, item.stem) or item
        ok, message = archive_item_to_reviewed(
            resolved, self.dataset_root, self.archive_log
        )
        if not ok:
            print(f"Archive failed: {message}", file=sys.stderr)
            self.status_message = message
            return
        self.reviewed.add(item.reviewed_key)
        self.index += 1
        self.status_message = ""
        self.persist()

    def current_resolved(self) -> QueueItem | None:
        item = self.current
        if item is None:
            return None
        resolved = resolve_queue_item(item, self.dataset_root)
        if resolved is not None and resolved != item:
            self.queue[self.index] = resolved
            return resolved
        return item

    def step_back(self) -> None:
        if self.index <= 0:
            self.status_message = "At first image; cannot go back."
            print("At first image; cannot go back.")
            self._refresh_display()
            return

        self.index -= 1
        item = self.current
        if item is None:
            return

        self.reviewed.discard(item.reviewed_key)
        ok, message, restored = restore_item_from_reviewed(
            item, self.dataset_root, self.archive_log
        )
        if restored is not None:
            self.queue[self.index] = restored
            item = restored
        else:
            resolved = resolve_queue_item(item, self.dataset_root)
            if resolved is not None:
                self.queue[self.index] = resolved
                item = resolved
            else:
                print(
                    f"Warning: could not restore or find stem={item.stem!r} split={item.split!r}: {message}",
                    file=sys.stderr,
                )

        self.status_message = "Stepped back for re-review."
        print(f"Step back -> [{self.index + 1}/{self.total}] {item.image_path.name}")
        self.persist()
        self._refresh_display()

    def status_line(self) -> str:
        item = self.current if self.index >= len(self.queue) else self.current_resolved()
        if item is None:
            return "All queued images reviewed. Press Q to exit."
        reviewed_count = len(self.reviewed)
        remaining = self.total - self.index
        label_status = "label OK" if item.label_path.is_file() else "missing label"
        view_label = "top" if item.current_view == VIEW_TOP else "oth"
        line = (
            f"[{self.index + 1}/{self.total}] {item.split}/{view_label} | "
            f"{item.image_path.name} | rem={remaining} | {label_status} | T/O/N/B/Q"
        )
        if self.status_message:
            line = f"{line} | {self.status_message}"
        return line

    def apply_view(self, target_view: str) -> None:
        item = self.current_resolved()
        if item is None:
            return

        target_folder = folder_for_view(item.split, target_view)  # type: ignore[arg-type]
        if target_folder == item.current_folder:
            print(f"Confirmed {target_view}: {item.image_path.name} (already in {target_folder})")
            self.status_message = f"Confirmed {target_view}."
            self.mark_reviewed(item)
            self._refresh_display()
            return

        ok, message, new_folder = try_move_item(item, self.dataset_root, target_view, self.moves_log)
        if not ok:
            print(f"Move failed: {message}", file=sys.stderr)
            self.status_message = message
            self._refresh_display()
            return

        if new_folder is not None:
            self.moves.append(
                {
                    "split": item.split,
                    "stem": item.stem,
                    "from": item.current_folder,
                    "to": new_folder,
                    "at": iso_now(),
                }
            )
        dest_image = self.dataset_root / IMAGES_ACTIVE_DIR / new_folder / item.image_path.name
        dest_label = self.dataset_root / LABELS_ACTIVE_DIR / new_folder / f"{item.stem}.txt"
        _split, new_view = FOLDER_TO_SPLIT_VIEW[new_folder]
        updated = replace(
            item,
            image_path=dest_image,
            label_path=dest_label,
            current_folder=new_folder,
            current_view=new_view,
        )
        self.queue[self.index] = updated
        print(f"Moved {item.image_path.name} -> {new_folder}")
        self.status_message = message
        self.mark_reviewed(updated)
        self._refresh_display()

    def advance_correct(self) -> None:
        item = self.current_resolved()
        if item is None:
            return
        print(f"Marked correct: {item.image_path.name}")
        self.mark_reviewed(item)
        self._refresh_display()

    def _refresh_display(self) -> None:
        import cv2

        item = self.current_resolved() if self.index < len(self.queue) else None
        line = self.status_line()
        if item is None:
            blank = 255 * cv2.ones((480, 640, 3), dtype=cv2.uint8)
            canvas, self.image_display_height = compose_display_with_footer(blank, line)
            cv2.imshow(WINDOW_NAME, canvas)
            return

        image = cv2.imread(str(item.image_path))
        if image is None:
            if not self.status_message:
                self.status_message = f"Failed to read: {item.image_path.name}"
            line = self.status_line()
            error_canvas = 255 * cv2.ones((480, 640, 3), dtype=cv2.uint8)
            canvas, self.image_display_height = compose_display_with_footer(error_canvas, line)
            cv2.imshow(WINDOW_NAME, canvas)
            return

        display = resize_for_display(image)
        canvas, self.image_display_height = compose_display_with_footer(display, line)
        cv2.imshow(WINDOW_NAME, canvas)


    def run(self) -> int:
        import cv2

        if not self.queue:
            print("Nothing to review (queue empty or all items already reviewed).")
            return 0

        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        self._refresh_display()

        print(f"Reviewing {self.total} images. Keys: T=top O=other N/Space=ok B=back Q=quit (keyboard only)")

        while True:
            key = read_key()
            if key < 0:
                continue
            if key in (ord("q"), ord("Q")):
                self.persist()
                print(f"Saved state to {self.state_path}")
                break

            if self.current is None:
                print("Review complete.")
                break

            if key in (ord("t"), ord("T")):
                self.apply_view(VIEW_TOP)
            elif key in (ord("o"), ord("O")):
                self.apply_view(VIEW_OTHER)
            elif key in (ord("n"), ord("N"), ord(" ")):
                self.advance_correct()
            elif key in (ord("b"), ord("B")):
                self.step_back()
            else:
                self.status_message = f"Unknown key {key!r}; use T O N Space B Q"
                self._refresh_display()

        cv2.destroyAllWindows()
        return 0


def main() -> int:
    args = parse_args()
    dataset_root = args.dataset_root.expanduser().resolve()
    if not (dataset_root / "images").is_dir():
        print(f"Missing images directory: {dataset_root / 'images'}", file=sys.stderr)
        return 1

    state_path = (
        args.state_file.expanduser().resolve()
        if args.state_file
        else dataset_root / DEFAULT_STATE_NAME
    )
    moves_log = (
        args.moves_log.expanduser().resolve()
        if args.moves_log
        else dataset_root / DEFAULT_MOVES_LOG_NAME
    )
    archive_log = dataset_root / ARCHIVE_LOG_NAME

    if args.reset and state_path.is_file():
        state_path.unlink()
        print(f"Cleared state: {state_path}")

    state = load_state(state_path)
    reviewed: set[tuple[str, str]] = state.get("_reviewed_set", set())
    moves: list[dict] = list(state.get("moves", []))

    saved_root = state.get("dataset_root", "")
    if saved_root and saved_root != str(dataset_root):
        print(
            f"Warning: state file dataset_root={saved_root!r} differs from "
            f"--dataset-root={dataset_root!r}",
            file=sys.stderr,
        )

    restore_dry_run = args.dry_run and args.restore_unreviewed_only
    if args.restore_unreviewed:
        restore_summary = restore_unreviewed_archived(
            dataset_root,
            args.splits,
            reviewed,
            archive_log=None if restore_dry_run else archive_log,
            dry_run=restore_dry_run,
        )
        print_restore_summary(restore_summary, dry_run=restore_dry_run)
        if restore_summary.failed:
            return 1
        if args.restore_unreviewed_only:
            return 0

    if args.start_at is not None:
        newly_marked, start_item = apply_start_at(
            dataset_root, args.splits, args.start_at, reviewed
        )
        save_state(state_path, dataset_root, reviewed, moves)
        print(
            f"--start-at {args.start_at}: marked {newly_marked} additional images reviewed "
            f"({args.start_at - 1} total before this position in full queue)."
        )
        if start_item is not None:
            full_count = len(build_queue(dataset_root, args.splits, set()))
            print(
                f"Starting at [{args.start_at}/{full_count}] "
                f"{start_item.split}/{start_item.current_folder} | {start_item.image_path.name}"
            )

    queue = build_queue(dataset_root, args.splits, reviewed)
    print(
        f"Queue: {len(queue)} images "
        f"(already reviewed: {len(reviewed)}, splits: {', '.join(args.splits)})"
    )

    try:
        import cv2  # noqa: F401
    except ImportError:
        print("opencv-python is required: pip install opencv-python", file=sys.stderr)
        return 1

    session = ReviewSession(
        dataset_root=dataset_root,
        queue=queue,
        state_path=state_path,
        moves_log=moves_log,
        archive_log=archive_log,
        reviewed=reviewed,
        moves=moves,
    )
    return session.run()


if __name__ == "__main__":
    raise SystemExit(main())
