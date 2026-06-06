#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
DEFAULT_DATASET_ROOT = Path("data/dataset_top")
DEFAULT_STATE_NAME = ".top_label_box_review.json"
WINDOW_NAME = "review top labels"


CLASS_COLORS_BGR = {
    0: (0, 255, 255),  # yellow
    1: (0, 255, 0),    # green
    2: (255, 0, 0),    # blue
    3: (0, 0, 255),    # red
}
DEFAULT_BOX_COLOR_BGR = (255, 255, 255)


@dataclass(frozen=True)
class ReviewItem:
    image_path: Path
    label_path: Path
    relative_image_path: Path
    relative_label_path: Path


@dataclass(frozen=True)
class YoloBox:
    class_id: int
    center_x: float
    center_y: float
    width: float
    height: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Review YOLO boxes for images in images_reviewed/*_top with matching labels. "
            "Press o for OK, n for not OK, q to quit."
        )
    )
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=DEFAULT_DATASET_ROOT,
        help="Dataset root containing images_reviewed/ and labels_reviewed/.",
    )
    parser.add_argument(
        "--images-dir",
        default="images_reviewed",
        help="Image directory under dataset root (default: images_reviewed).",
    )
    parser.add_argument(
        "--labels-dir",
        default="labels_reviewed",
        help="Label directory under dataset root (default: labels_reviewed).",
    )
    parser.add_argument(
        "--not-ok-dir",
        default="not_ok",
        help="Folder under dataset root where rejected image/label pairs are moved.",
    )
    parser.add_argument(
        "--state-file",
        type=Path,
        default=None,
        help="JSON file used to remember OK images. Default: dataset_root/.top_label_box_review.json.",
    )
    parser.add_argument(
        "--include-empty-labels",
        action="store_true",
        help="Include images with an existing but empty label file.",
    )
    parser.add_argument(
        "--reset-state",
        action="store_true",
        help="Ignore previous OK decisions and rebuild the review queue.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed used to present images in random order (default: 42).",
    )
    return parser.parse_args()


def load_state(state_path: Path, *, reset_state: bool) -> dict[str, Any]:
    if reset_state or not state_path.exists():
        return {"ok": []}
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"Warning: could not parse state file: {state_path}", file=sys.stderr)
        return {"ok": []}
    if not isinstance(data, dict):
        return {"ok": []}
    ok_items = data.get("ok", [])
    if not isinstance(ok_items, list):
        data["ok"] = []
    return data


def save_state(state_path: Path, state: dict[str, Any]) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def is_top_folder(path: Path) -> bool:
    return any(part.endswith("_top") for part in path.parts)


def iter_images(images_root: Path) -> Iterable[Path]:
    for image_path in sorted(images_root.rglob("*")):
        if image_path.is_file() and image_path.suffix.lower() in IMAGE_EXTENSIONS:
            yield image_path


def find_review_items(
    *,
    dataset_root: Path,
    images_dir: str,
    labels_dir: str,
    include_empty_labels: bool,
    ok_relative_images: set[str],
) -> list[ReviewItem]:
    images_root = dataset_root / images_dir
    labels_root = dataset_root / labels_dir
    if not images_root.exists():
        raise FileNotFoundError(f"Image root does not exist: {images_root}")
    if not labels_root.exists():
        raise FileNotFoundError(f"Label root does not exist: {labels_root}")

    items: list[ReviewItem] = []
    missing_labels = 0
    skipped_empty_labels = 0

    for image_path in iter_images(images_root):
        relative_image_path = image_path.relative_to(images_root)
        if not is_top_folder(relative_image_path):
            continue
        if relative_image_path.as_posix() in ok_relative_images:
            continue

        relative_label_path = relative_image_path.with_suffix(".txt")
        label_path = labels_root / relative_label_path
        if not label_path.exists():
            missing_labels += 1
            continue
        if not include_empty_labels and label_path.stat().st_size == 0:
            skipped_empty_labels += 1
            continue

        items.append(
            ReviewItem(
                image_path=image_path,
                label_path=label_path,
                relative_image_path=relative_image_path,
                relative_label_path=relative_label_path,
            )
        )

    if missing_labels:
        print(f"Skipped {missing_labels} images without matching labels.", file=sys.stderr)
    if skipped_empty_labels:
        print(
            f"Skipped {skipped_empty_labels} images with empty label files "
            "(use --include-empty-labels to review them).",
            file=sys.stderr,
        )
    return items


def read_yolo_boxes(label_path: Path) -> list[YoloBox]:
    boxes: list[YoloBox] = []
    for line_number, line in enumerate(label_path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split()
        if len(parts) < 5:
            print(f"Warning: invalid label line {label_path}:{line_number}: {line}", file=sys.stderr)
            continue
        try:
            class_id = int(float(parts[0]))
            center_x = float(parts[1])
            center_y = float(parts[2])
            width = float(parts[3])
            height = float(parts[4])
        except ValueError:
            print(f"Warning: invalid label line {label_path}:{line_number}: {line}", file=sys.stderr)
            continue
        boxes.append(YoloBox(class_id, center_x, center_y, width, height))
    return boxes


def draw_boxes(image: Any, boxes: list[YoloBox]) -> Any:
    import cv2

    canvas = image.copy()
    image_height, image_width = canvas.shape[:2]
    for box in boxes:
        x1 = int((box.center_x - box.width / 2.0) * image_width)
        y1 = int((box.center_y - box.height / 2.0) * image_height)
        x2 = int((box.center_x + box.width / 2.0) * image_width)
        y2 = int((box.center_y + box.height / 2.0) * image_height)

        x1 = max(0, min(image_width - 1, x1))
        y1 = max(0, min(image_height - 1, y1))
        x2 = max(0, min(image_width - 1, x2))
        y2 = max(0, min(image_height - 1, y2))

        color = CLASS_COLORS_BGR.get(box.class_id, DEFAULT_BOX_COLOR_BGR)
        cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            canvas,
            str(box.class_id),
            (x1, max(16, y1 - 6)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2,
            cv2.LINE_AA,
        )
    return canvas


def add_overlay(image: Any, *, text: str) -> Any:
    import cv2

    canvas = image.copy()
    cv2.rectangle(canvas, (0, 0), (canvas.shape[1], 36), (0, 0, 0), -1)
    cv2.putText(
        canvas,
        text,
        (10, 24),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )
    return canvas


def move_to_not_ok(item: ReviewItem, *, dataset_root: Path, images_dir: str, labels_dir: str, not_ok_dir: str) -> None:
    image_target = dataset_root / not_ok_dir / images_dir / item.relative_image_path
    label_target = dataset_root / not_ok_dir / labels_dir / item.relative_label_path
    image_target.parent.mkdir(parents=True, exist_ok=True)
    label_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(item.image_path), str(image_target))
    shutil.move(str(item.label_path), str(label_target))


def restore_from_not_ok(item: ReviewItem, *, dataset_root: Path, images_dir: str, labels_dir: str, not_ok_dir: str) -> None:
    image_source = dataset_root / not_ok_dir / images_dir / item.relative_image_path
    label_source = dataset_root / not_ok_dir / labels_dir / item.relative_label_path
    if image_source.exists():
        item.image_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(image_source), str(item.image_path))
    if label_source.exists():
        item.label_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(label_source), str(item.label_path))


def undo_decision(
    item: ReviewItem,
    decision: str,
    *,
    dataset_root: Path,
    images_dir: str,
    labels_dir: str,
    not_ok_dir: str,
    ok_relative_images: set[str],
) -> None:
    ok_relative_images.discard(item.relative_image_path.as_posix())
    if decision == "not_ok":
        restore_from_not_ok(
            item,
            dataset_root=dataset_root,
            images_dir=images_dir,
            labels_dir=labels_dir,
            not_ok_dir=not_ok_dir,
        )


def main() -> int:
    args = parse_args()
    dataset_root = args.dataset_root.expanduser().resolve()
    state_path = (
        args.state_file.expanduser().resolve()
        if args.state_file is not None
        else dataset_root / DEFAULT_STATE_NAME
    )
    state = load_state(state_path, reset_state=bool(args.reset_state))
    ok_relative_images = set(str(path) for path in state.get("ok", []))

    try:
        import cv2
    except ImportError:
        print("Missing dependency: opencv-python", file=sys.stderr)
        print("Install with: source .venv/bin/activate && python3 -m pip install opencv-python", file=sys.stderr)
        return 2

    try:
        items = find_review_items(
            dataset_root=dataset_root,
            images_dir=str(args.images_dir),
            labels_dir=str(args.labels_dir),
            include_empty_labels=bool(args.include_empty_labels),
            ok_relative_images=ok_relative_images,
        )
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not items:
        print("No matching images found for review.")
        return 0

    random.Random(int(args.seed)).shuffle(items)
    print(f"Reviewing {len(items)} image/label pairs.")
    print("Keys: o = OK, n = not OK (move to not_ok), q/Esc = quit")

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    index = 0
    decisions: dict[str, str] = {}
    try:
        while index < len(items):
            item = items[index]
            image = cv2.imread(str(item.image_path))
            if image is None:
                print(f"Warning: could not read image: {item.image_path}", file=sys.stderr)
                index += 1
                continue

            boxes = read_yolo_boxes(item.label_path)
            display = draw_boxes(image, boxes)
            display = add_overlay(
                display,
                text=(
                    f"{index + 1}/{len(items)} {item.relative_image_path.as_posix()} "
                    "| o=OK n=not OK b=back q=quit"
                ),
            )
            cv2.imshow(WINDOW_NAME, display)

            while True:
                key = cv2.waitKey(0) & 0xFF
                if key in (ord("q"), 27):
                    save_state(state_path, state)
                    return 0
                if key == ord("b"):
                    if index == 0:
                        print("Already at first image.")
                        continue
                    index -= 1
                    previous_item = items[index]
                    previous_key = previous_item.relative_image_path.as_posix()
                    previous_decision = decisions.pop(previous_key, "")
                    undo_decision(
                        previous_item,
                        previous_decision,
                        dataset_root=dataset_root,
                        images_dir=str(args.images_dir),
                        labels_dir=str(args.labels_dir),
                        not_ok_dir=str(args.not_ok_dir),
                        ok_relative_images=ok_relative_images,
                    )
                    state["ok"] = sorted(ok_relative_images)
                    save_state(state_path, state)
                    break
                if key == ord("o"):
                    item_key = item.relative_image_path.as_posix()
                    ok_relative_images.add(item_key)
                    decisions[item_key] = "ok"
                    state["ok"] = sorted(ok_relative_images)
                    save_state(state_path, state)
                    index += 1
                    break
                if key == ord("n"):
                    item_key = item.relative_image_path.as_posix()
                    move_to_not_ok(
                        item,
                        dataset_root=dataset_root,
                        images_dir=str(args.images_dir),
                        labels_dir=str(args.labels_dir),
                        not_ok_dir=str(args.not_ok_dir),
                    )
                    ok_relative_images.discard(item_key)
                    decisions[item_key] = "not_ok"
                    state["ok"] = sorted(ok_relative_images)
                    save_state(state_path, state)
                    index += 1
                    break
    finally:
        cv2.destroyAllWindows()

    print("Review complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
