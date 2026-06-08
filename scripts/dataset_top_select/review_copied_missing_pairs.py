#!/usr/bin/env python3
"""
Review copied missing pairs (manifest batch not yet in test_train_val subset).

OpenCV UI modeled on review_folder_placement.py:
  K or T  — top-down, KEEP in both dataset folders
  R O N Space — not top-down, MOVE out of both datasets into review/removed/
  B — step back (undo last decision, restore files if removed)
  Q — save and quit

State: data/copied_missing_pairs/.review_copied_missing.json
Keep list: data/copied_missing_pairs/keep_topdown.json (synced on every decision)

Example:
  source .venv/bin/activate
  pip install opencv-python
  python scripts/dataset_top_select/review_copied_missing_pairs.py
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = WORKSPACE_ROOT / "data/copied_missing_pairs/manifest.csv"
DEFAULT_REVIEW_ROOT = WORKSPACE_ROOT / "data/copied_missing_pairs"
DEFAULT_STATE_NAME = ".review_copied_missing.json"
DEFAULT_KEPT_JSON = DEFAULT_REVIEW_ROOT / "keep_topdown.json"
DEFAULT_REJECT_JSON = DEFAULT_REVIEW_ROOT / "reject_non_topdown.json"
DEFAULT_KEEP_TXT = DEFAULT_REVIEW_ROOT / "keep_topdown.txt"
DEFAULT_REMOVE_TXT = DEFAULT_REVIEW_ROOT / "remove_non_topdown.txt"
REMOVED_DIR_NAME = "review/removed"
WINDOW_NAME = "copied missing pairs — top-down review"
MAX_DISPLAY_WIDTH = 1280
FOOTER_HEIGHT = 40
FOOTER_BG_COLOR = (40, 40, 40)
STATE_VERSION = 1
Decision = Literal["keep", "remove"]


@dataclass(frozen=True)
class ManifestItem:
    split: str
    class_name: str
    stem: str
    image_il: Path
    label_il: Path
    image_ttv: Path
    label_ttv: Path

    def path_roles(self) -> tuple[tuple[str, Path], ...]:
        return (
            ("il_image", self.image_il),
            ("il_label", self.label_il),
            ("ttv_image", self.image_ttv),
            ("ttv_label", self.label_ttv),
        )


def iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Review copied missing pairs: keep top-down, remove others (OpenCV).",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help=f"CSV manifest (default: {DEFAULT_MANIFEST.relative_to(WORKSPACE_ROOT)}).",
    )
    parser.add_argument(
        "--review-root",
        type=Path,
        default=DEFAULT_REVIEW_ROOT,
        help="Root for state, keep json, and review/removed/ staging.",
    )
    parser.add_argument(
        "--state-file",
        type=Path,
        default=None,
        help=f"Review state JSON (default: <review-root>/{DEFAULT_STATE_NAME}).",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear review state (does not restore files from review/removed/).",
    )
    parser.add_argument(
        "--import-kept",
        action="store_true",
        default=True,
        help="Import stems from keep_topdown.json as already reviewed keep (default: on).",
    )
    parser.add_argument(
        "--no-import-kept",
        action="store_false",
        dest="import_kept",
        help="Do not pre-load keep_topdown.json into reviewed state.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log moves but do not modify files.",
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Print queue counts and exit (no UI).",
    )
    return parser.parse_args()


def load_manifest(path: Path) -> list[ManifestItem]:
    items: list[ManifestItem] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            items.append(
                ManifestItem(
                    split=row["split"],
                    class_name=row["class"],
                    stem=row["stem"],
                    image_il=Path(row["image_il"]),
                    label_il=Path(row["label_il"]),
                    image_ttv=Path(row["image_ttv"]),
                    label_ttv=Path(row["label_ttv"]),
                )
            )
    # Keep manifest.csv row order (same sequence as the web reviewer).
    return items


def removed_staging_path(review_root: Path, original: Path) -> Path:
    try:
        rel = original.resolve().relative_to(WORKSPACE_ROOT.resolve())
    except ValueError:
        rel = Path(original.name)
    return review_root / REMOVED_DIR_NAME / rel


def load_state(state_path: Path) -> dict:
    if not state_path.is_file():
        return {
            "version": STATE_VERSION,
            "manifest": "",
            "decisions": {},
            "history": [],
        }
    data = json.loads(state_path.read_text(encoding="utf-8"))
    data["decisions"] = dict(data.get("decisions", {}))
    return data


def save_state(
    state_path: Path,
    manifest_path: Path,
    decisions: dict[str, str],
    history: list[dict],
    *,
    queue_index: int | None = None,
    resume_stem: str | None = None,
) -> None:
    payload = {
        "version": STATE_VERSION,
        "manifest": str(manifest_path.resolve()),
        "updated_at": iso_now(),
        "decisions": decisions,
        "history": history[-500:],
        "kept_count": sum(1 for value in decisions.values() if value == "keep"),
        "remove_count": sum(1 for value in decisions.values() if value == "remove"),
        "queue_index": queue_index,
        "resume_stem": resume_stem,
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def export_sidecar_lists(rows: list[ManifestItem], decisions: dict[str, str]) -> None:
    by_stem = {row.stem: row for row in rows}
    kept = {stem for stem, decision in decisions.items() if decision == "keep"}
    remove_stems = [row.stem for row in rows if row.stem not in kept]

    kept_payload = {
        "updated_at": iso_now(),
        "kept_stems": sorted(kept),
        "count": len(kept),
    }
    DEFAULT_KEPT_JSON.write_text(json.dumps(kept_payload, indent=2) + "\n", encoding="utf-8")

    keep_lines = ["# Top-down samples kept in both dataset folders", f"# count: {len(kept)}", ""]
    for stem in sorted(kept):
        row = by_stem[stem]
        keep_lines.append(f"{row.split}\t{row.class_name}\t{stem}\t{row.image_il}")
    DEFAULT_KEEP_TXT.write_text("\n".join(keep_lines) + "\n", encoding="utf-8")

    remove_lines = ["# Samples removed from both dataset folders", f"# count: {len(remove_stems)}", ""]
    for stem in sorted(remove_stems):
        row = by_stem[stem]
        remove_lines.append(f"{row.split}\t{row.class_name}\t{stem}\t{row.image_il}")
    DEFAULT_REMOVE_TXT.write_text("\n".join(remove_lines) + "\n", encoding="utf-8")


def stems_in_removed_staging(review_root: Path, manifest_stems: set[str]) -> set[str]:
    removed_root = review_root / REMOVED_DIR_NAME
    if not removed_root.is_dir():
        return set()
    found: set[str] = set()
    for image_path in removed_root.rglob("*.jpg"):
        stem = image_path.stem
        if stem in manifest_stems:
            found.add(stem)
    return found


def merge_decisions(
    manifest_stems: set[str],
    review_root: Path,
    history: list[dict],
    *,
    import_kept: bool,
) -> tuple[dict[str, str], dict[str, int]]:
    """Rebuild decisions from every persisted source (keep wins over remove)."""
    decisions: dict[str, str] = {}
    stats = {"from_keep_json": 0, "from_staging": 0, "from_reject_json": 0, "from_history": 0}

    if import_kept and DEFAULT_KEPT_JSON.is_file():
        data = json.loads(DEFAULT_KEPT_JSON.read_text(encoding="utf-8"))
        for stem in data.get("kept_stems", []):
            if stem in manifest_stems:
                decisions[stem] = "keep"
                stats["from_keep_json"] += 1

    for stem in stems_in_removed_staging(review_root, manifest_stems):
        if decisions.get(stem) != "keep":
            decisions[stem] = "remove"
            stats["from_staging"] += 1

    if DEFAULT_REJECT_JSON.is_file():
        data = json.loads(DEFAULT_REJECT_JSON.read_text(encoding="utf-8"))
        for stem in data.get("rejected_stems", []):
            if stem in manifest_stems and decisions.get(stem) != "keep":
                if decisions.get(stem) != "remove":
                    stats["from_reject_json"] += 1
                decisions[stem] = "remove"

    for entry in history:
        stem = entry.get("stem")
        decision = entry.get("decision")
        if stem in manifest_stems and decision in ("keep", "remove"):
            if decisions.get(stem) != decision:
                stats["from_history"] += 1
            decisions[stem] = decision

    return decisions, stats


def resolve_queue_index(
    rows: list[ManifestItem],
    queue: list[ManifestItem],
    resume_stem: str | None,
    saved_index: int | None,
) -> int:
    if not queue:
        return 0
    if resume_stem:
        for index, item in enumerate(queue):
            if item.stem == resume_stem:
                return index
        # resume_stem was already decided; continue at next pending after it in manifest order.
        manifest_index = next((i for i, row in enumerate(rows) if row.stem == resume_stem), None)
        if manifest_index is not None:
            for row in rows[manifest_index + 1 :]:
                for index, item in enumerate(queue):
                    if item.stem == row.stem:
                        return index
    if saved_index is not None:
        return min(max(0, saved_index), len(queue) - 1)
    return 0


def move_to_removed(item: ManifestItem, review_root: Path, dry_run: bool) -> list[str]:
    errors: list[str] = []
    for _role, path in item.path_roles():
        if not path.is_file():
            continue
        dest = removed_staging_path(review_root, path)
        if dry_run:
            print(f"[dry-run] remove {path} -> {dest}")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            path.unlink()
            continue
        shutil.move(str(path), str(dest))
    return errors


def restore_from_removed(item: ManifestItem, review_root: Path, dry_run: bool) -> list[str]:
    errors: list[str] = []
    for _role, original in item.path_roles():
        staging = removed_staging_path(review_root, original)
        if not staging.is_file():
            if original.is_file():
                continue
            errors.append(f"missing staging and original: {original}")
            continue
        if dry_run:
            print(f"[dry-run] restore {staging} -> {original}")
            continue
        original.parent.mkdir(parents=True, exist_ok=True)
        if original.exists():
            staging.unlink()
            continue
        shutil.move(str(staging), str(original))
    return errors


def build_queue(rows: list[ManifestItem], decisions: dict[str, str]) -> list[ManifestItem]:
    return [row for row in rows if row.stem not in decisions]


def count_decisions(decisions: dict[str, str]) -> tuple[int, int]:
    kept = sum(1 for value in decisions.values() if value == "keep")
    removed = sum(1 for value in decisions.values() if value == "remove")
    return kept, removed


def read_yolo_boxes(label_path: Path) -> list[tuple[int, float, float, float, float]]:
    if not label_path.is_file():
        return []
    boxes: list[tuple[int, float, float, float, float]] = []
    for line in label_path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) < 5:
            continue
        boxes.append((int(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])))
    return boxes


def draw_boxes(image, label_path: Path, class_name: str):
    import cv2

    boxes = read_yolo_boxes(label_path)
    if not boxes:
        return image
    height, width = image.shape[:2]
    colors = {0: (0, 255, 0), 1: (255, 128, 0)}
    names = {"vcra": 0, "vvel": 1}
    for class_id, cx, cy, bw, bh in boxes:
        box_w = int(bw * width)
        box_h = int(bh * height)
        x = int(cx * width - box_w / 2)
        y = int(cy * height - box_h / 2)
        color = colors.get(class_id, (0, 255, 255))
        cv2.rectangle(image, (x, y), (x + box_w, y + box_h), color, 2)
        name = class_name if class_id == names.get(class_name, class_id) else str(class_id)
        cv2.putText(image, name, (x + 4, max(y + 16, 16)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
    return image


def resize_for_display(image, max_width: int = MAX_DISPLAY_WIDTH):
    import cv2

    height, width = image.shape[:2]
    if width <= max_width:
        return image
    scale = max_width / width
    return cv2.resize(image, (max_width, int(height * scale)), interpolation=cv2.INTER_AREA)


def compose_display_with_footer(image, status_line: str):
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
    text_y = height + (FOOTER_HEIGHT + text_size[1]) // 2
    cv2.putText(canvas, status_line, (10, text_y), font, scale, (255, 255, 255), thickness, cv2.LINE_AA)
    return canvas


def read_key() -> int:
    import sys
    import cv2

    if sys.platform == "darwin":
        key = cv2.waitKeyEx(0)
    else:
        key = cv2.waitKey(0)
    return -1 if key < 0 else key & 0xFF


def resolve_label_path(item: ManifestItem, review_root: Path) -> Path:
    if item.label_il.is_file():
        return item.label_il
    staging = removed_staging_path(review_root, item.label_il)
    return staging if staging.is_file() else item.label_il


def resolve_image_path(item: ManifestItem, review_root: Path) -> Path:
    if item.image_il.is_file():
        return item.image_il
    staging = removed_staging_path(review_root, item.image_il)
    return staging if staging.is_file() else item.image_il


class ReviewSession:
    def __init__(
        self,
        rows: list[ManifestItem],
        queue: list[ManifestItem],
        review_root: Path,
        manifest_path: Path,
        state_path: Path,
        decisions: dict[str, str],
        history: list[dict],
        dry_run: bool,
        start_index: int = 0,
    ) -> None:
        self.rows = rows
        self.queue = queue
        self.review_root = review_root
        self.manifest_path = manifest_path
        self.state_path = state_path
        self.decisions = decisions
        self.history = history
        self.dry_run = dry_run
        self.index = start_index
        self.status_message = ""
        self.total_manifest = len(rows)

    @property
    def current(self) -> ManifestItem | None:
        if self.index >= len(self.queue):
            return None
        return self.queue[self.index]

    def persist(self) -> None:
        current = self.current
        save_state(
            self.state_path,
            self.manifest_path,
            self.decisions,
            self.history,
            queue_index=self.index,
            resume_stem=current.stem if current else None,
        )
        export_sidecar_lists(self.rows, self.decisions)

    def status_line(self) -> str:
        item = self.current
        kept, removed = count_decisions(self.decisions)
        pending = len(self.queue) - self.index
        if item is None:
            return f"Done. kept={kept} remove={removed} total={self.total_manifest} | Q=quit"
        image_path = resolve_image_path(item, self.review_root)
        label_ok = "label OK" if resolve_label_path(item, self.review_root).is_file() else "no label"
        line = (
            f"[{self.index + 1}/{len(self.queue)}] {item.split}/{item.class_name} | "
            f"{image_path.name} | kept={kept} remove={removed} pending={pending} | "
            f"K/T=keep R/Space=remove B=back Q=quit | {label_ok}"
        )
        return f"{line} | {self.status_message}" if self.status_message else line

    def apply_decision(self, decision: Decision) -> None:
        item = self.current
        if item is None:
            return
        if item.stem in self.decisions:
            print(f"Skip already reviewed: {item.stem} ({self.decisions[item.stem]})")
            self.index += 1
            self.persist()
            self._refresh_display()
            return
        if decision == "keep":
            print(f"KEEP (top-down): {item.stem}")
            self.status_message = "Kept in datasets."
        else:
            move_to_removed(item, self.review_root, self.dry_run)
            self.status_message = "Moved to review/removed/."
            print(f"REMOVE: {item.stem}")
        self.decisions[item.stem] = decision
        self.history.append({"stem": item.stem, "decision": decision, "at": iso_now()})
        self.index += 1
        self.persist()
        self._refresh_display()

    def step_back(self) -> None:
        if not self.history:
            self.status_message = "Nothing to undo."
            self._refresh_display()
            return
        last = self.history.pop()
        stem = last["stem"]
        decision = last["decision"]
        item = next(row for row in self.rows if row.stem == stem)
        if decision == "remove":
            errors = restore_from_removed(item, self.review_root, self.dry_run)
            self.status_message = f"Undo partial: {errors[0]}" if errors else "Restored from review/removed/."
        else:
            self.status_message = "Undo keep (still in datasets)."
        self.decisions.pop(stem, None)
        self.queue.insert(self.index, item)
        print(f"Undo {decision}: {stem}")
        self.persist()
        self._refresh_display()

    def _refresh_display(self) -> None:
        import cv2

        item = self.current
        line = self.status_line()
        if item is None:
            blank = 255 * cv2.ones((480, 640, 3), dtype=cv2.uint8)
            cv2.imshow(WINDOW_NAME, compose_display_with_footer(blank, line))
            return
        image_path = resolve_image_path(item, self.review_root)
        label_path = resolve_label_path(item, self.review_root)
        image = cv2.imread(str(image_path))
        if image is None:
            self.status_message = f"Cannot read {image_path.name}"
            blank = 255 * cv2.ones((480, 640, 3), dtype=cv2.uint8)
            cv2.imshow(WINDOW_NAME, compose_display_with_footer(blank, self.status_line()))
            return
        image = draw_boxes(image, label_path, item.class_name)
        cv2.imshow(WINDOW_NAME, compose_display_with_footer(resize_for_display(image), line))

    def run(self) -> int:
        import cv2

        if not self.queue:
            kept, removed = count_decisions(self.decisions)
            print(f"Nothing left to review ({kept} kept, {removed} removed, {self.total_manifest} total).")
            return 0
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        self._refresh_display()
        kept, removed = count_decisions(self.decisions)
        print(f"Queue: {len(self.queue)} pending ({kept} kept, {removed} removed). Keys: K/T R/Space B Q")
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
            if key in (ord("k"), ord("K"), ord("t"), ord("T")):
                self.apply_decision("keep")
            elif key in (ord("r"), ord("R"), ord("o"), ord("O"), ord("n"), ord("N"), ord(" ")):
                self.apply_decision("remove")
            elif key in (ord("b"), ord("B")):
                self.step_back()
            else:
                self.status_message = "Unknown key; use K T R Space B Q"
                self._refresh_display()
        cv2.destroyAllWindows()
        kept, removed = count_decisions(self.decisions)
        print(f"Final: kept={kept} remove={removed} pending={self.total_manifest - kept - removed}")
        return 0


def main() -> int:
    args = parse_args()
    manifest_path = args.manifest.expanduser().resolve()
    review_root = args.review_root.expanduser().resolve()
    state_path = args.state_file.expanduser().resolve() if args.state_file else review_root / DEFAULT_STATE_NAME
    if not manifest_path.is_file():
        print(f"Manifest not found: {manifest_path}", file=sys.stderr)
        return 1
    try:
        import cv2  # noqa: F401
    except ImportError:
        print("opencv-python is required: pip install opencv-python", file=sys.stderr)
        return 1
    rows = load_manifest(manifest_path)
    manifest_stems = {row.stem for row in rows}
    if args.reset and state_path.is_file():
        state_path.unlink()
        print(f"Cleared state: {state_path}")
    state = load_state(state_path)
    history: list[dict] = list(state.get("history", []))
    decisions, merge_stats = merge_decisions(
        manifest_stems,
        review_root,
        history,
        import_kept=args.import_kept,
    )
    if any(merge_stats.values()):
        print(
            "Merged review state:"
            f" keep_json={merge_stats['from_keep_json']}"
            f" staging={merge_stats['from_staging']}"
            f" reject_json={merge_stats['from_reject_json']}"
            f" history={merge_stats['from_history']}"
        )
    for row in rows:
        if decisions.get(row.stem) == "remove":
            if any(path.is_file() for _role, path in row.path_roles()):
                move_to_removed(row, review_root, args.dry_run)
    queue = build_queue(rows, decisions)
    start_index = resolve_queue_index(
        rows,
        queue,
        state.get("resume_stem"),
        state.get("queue_index"),
    )
    export_sidecar_lists(rows, decisions)
    save_state(
        state_path,
        manifest_path,
        decisions,
        history,
        queue_index=start_index,
        resume_stem=queue[start_index].stem if queue else None,
    )
    kept, removed = count_decisions(decisions)
    if args.stats_only:
        print(
            f"Manifest: {len(rows)} | kept: {kept} | removed: {removed} | "
            f"pending: {len(queue)} | resume: {start_index + 1 if queue else 0}/{len(queue)} | "
            f"review_root: {review_root}"
        )
        return 0
    session = ReviewSession(
        rows=rows,
        queue=queue,
        review_root=review_root,
        manifest_path=manifest_path,
        state_path=state_path,
        decisions=decisions,
        history=history,
        dry_run=args.dry_run,
        start_index=start_index,
    )
    return session.run()


if __name__ == "__main__":
    raise SystemExit(main())
