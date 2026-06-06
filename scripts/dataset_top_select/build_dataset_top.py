#!/usr/bin/env python3
"""
Build a YOLO dataset with physical folders for top vs other (per source split).

Source layout (unchanged):
  <source>/images/{train,val,test} and <source>/labels/{train,val,test}

Output layout under --output:
  images/{train_top,train_oth,train_null,val_top,val_other,val_null,test_top,test_oth,test_null}
  labels/<same subfolder names>

- *NULL*.jpg (case-insensitive NULL in stem, .jpg only): copy without running the model
  into {split}_null.
- Other images: require a matching .txt label, run best.pt; copy image + original label
  into exactly one folder based on the **highest-confidence** predicted box at or above
  --confidence (Ultralytics predict already applies conf). Class ids are resolved from
  model.names (expects top vs other / oth).

Note: val's non-top folder is named val_other; train and test use train_oth and test_oth
as requested.

Training stack note: Colab / project training is pinned to Python 3.11; pin ultralytics
in the environment you use to run this script.

Example:
  source .venv/bin/activate
  python scripts/dataset_top_select/build_dataset_top.py \\
    --weights /path/to/best.pt \\
    --source /path/to/dataset_images_labels \\
    --output data/dataset_top \\
    --device mps
"""

from __future__ import annotations

import argparse
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable

NON_NULL_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

SOURCE_SPLITS = ("train", "val", "test")

PREDICT_BATCH = 32


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Class-split YOLO dataset copy using best.pt (physical top/other folders).",
    )
    parser.add_argument(
        "--weights",
        type=Path,
        required=True,
        help="Path to YOLO weights (e.g. best.pt).",
    )
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Root containing images/{train,val,test} and labels/{train,val,test}.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/dataset_top"),
        help="Destination root (default: data/dataset_top).",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.25,
        help="Minimum confidence for boxes kept by predict(); routing uses max conf among them.",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help='Torch device, e.g. "cpu", "mps", or "0" for first CUDA device.',
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print summary without copying files (inference still runs for non-NULL).",
    )
    parser.add_argument(
        "--strict-labels",
        action="store_true",
        help="Exit with error if a NULL image has no matching .txt label.",
    )
    return parser.parse_args()


def is_null_jpg(path: Path) -> bool:
    return path.suffix.lower() == ".jpg" and "null" in path.stem.lower()


def list_non_null_images(images_dir: Path) -> list[Path]:
    if not images_dir.is_dir():
        return []
    out: list[Path] = []
    for path in sorted(images_dir.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in NON_NULL_IMAGE_SUFFIXES:
            continue
        if is_null_jpg(path):
            continue
        out.append(path)
    return out


def list_null_jpgs(images_dir: Path) -> list[Path]:
    if not images_dir.is_dir():
        return []
    return sorted(p for p in images_dir.iterdir() if p.is_file() and is_null_jpg(p))


def validate_source_layout(source: Path) -> None:
    for name in ("images", "labels"):
        root = source / name
        if not root.is_dir():
            raise SystemExit(f"Missing directory: {root}")
    for split in SOURCE_SPLITS:
        for name in ("images", "labels"):
            sub = source / name / split
            if not sub.is_dir():
                raise SystemExit(f"Missing split directory: {sub}")


def chunked(items: list[Path], size: int) -> Iterable[list[Path]]:
    for index in range(0, len(items), size):
        yield items[index : index + size]


def copy_pair(
    image_path: Path,
    label_path: Path | None,
    out_image: Path,
    out_label: Path,
    dry_run: bool,
) -> None:
    if dry_run:
        return
    out_image.parent.mkdir(parents=True, exist_ok=True)
    out_label.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(image_path, out_image)
    if label_path is not None and label_path.is_file():
        shutil.copy2(label_path, out_label)


def register_collision(
    registry: dict[tuple[str, str], Path],
    destination_subfolder: str,
    image_path: Path,
    collision_count: list[int],
) -> None:
    key = (destination_subfolder, image_path.name)
    if key in registry:
        print(
            f"Warning: duplicate output name {image_path.name!r} in {destination_subfolder!r}; "
            f"first {registry[key]} then {image_path} (last wins).",
            file=sys.stderr,
        )
        collision_count[0] += 1
    registry[key] = image_path


def null_destination_subfolder(source_split: str) -> str:
    return f"{source_split}_null"


def other_destination_subfolder(source_split: str) -> str:
    if source_split == "val":
        return "val_other"
    return f"{source_split}_oth"


def top_destination_subfolder(source_split: str) -> str:
    return f"{source_split}_top"


def resolve_top_other_class_ids(names: dict | list) -> tuple[int, int]:
    """Return (top_class_id, other_class_id) from model.names."""
    if isinstance(names, list):
        mapping = {index: str(name) for index, name in enumerate(names)}
    else:
        mapping = {int(index): str(label) for index, label in names.items()}

    top_id: int | None = None
    other_id: int | None = None
    for class_id, raw in mapping.items():
        label_lower = raw.strip().lower()
        if label_lower == "top" or label_lower.endswith("_top"):
            if top_id is None:
                top_id = class_id
        elif (
            label_lower in ("other", "oth")
            or label_lower.endswith("_other")
            or label_lower.endswith("_oth")
        ):
            if other_id is None:
                other_id = class_id

    if top_id is None or other_id is None:
        raise SystemExit(
            "Could not resolve class ids for top/other from model.names="
            f"{mapping!r}. Use standard names 'top' and 'other' (or 'oth') in the trained model."
        )
    if top_id == other_id:
        raise SystemExit(f"Invalid model.names: top and other map to same id {top_id}.")
    return top_id, other_id


def destination_for_prediction(
    source_split: str,
    predicted_class_id: int,
    top_class_id: int,
    other_class_id: int,
) -> str:
    if predicted_class_id == top_class_id:
        return top_destination_subfolder(source_split)
    if predicted_class_id == other_class_id:
        return other_destination_subfolder(source_split)
    raise SystemExit(
        f"Predicted class id {predicted_class_id} is not top ({top_class_id}) "
        f"or other ({other_class_id})."
    )


def main() -> None:
    args = parse_args()
    source = args.source.expanduser().resolve()
    output = args.output.expanduser().resolve()
    weights = args.weights.expanduser().resolve()

    validate_source_layout(source)

    if not weights.is_file():
        raise SystemExit(f"Weights not found: {weights}")

    stats: defaultdict[str, int] = defaultdict(int)
    collision_count = [0]
    registry: dict[tuple[str, str], Path] = {}

    non_null_jobs: list[tuple[Path, Path, str]] = []

    for source_split in SOURCE_SPLITS:
        images_dir = source / "images" / source_split
        labels_dir = source / "labels" / source_split
        null_sub = null_destination_subfolder(source_split)
        out_img_null = output / "images" / null_sub
        out_lbl_null = output / "labels" / null_sub

        for null_path in list_null_jpgs(images_dir):
            label_candidate = labels_dir / f"{null_path.stem}.txt"
            register_collision(registry, null_sub, null_path, collision_count)
            if args.strict_labels and not label_candidate.is_file():
                raise SystemExit(f"Missing label for NULL image: {label_candidate}")
            if not label_candidate.is_file():
                print(
                    f"Warning: NULL image without label, copying image only: {null_path}",
                    file=sys.stderr,
                )
                stats["null_missing_label"] += 1
            copy_pair(
                null_path,
                label_candidate if label_candidate.is_file() else None,
                out_img_null / null_path.name,
                out_lbl_null / f"{null_path.stem}.txt",
                args.dry_run,
            )
            stats["null_copied"] += 1
            stats[f"dest_{null_sub}"] += 1

        for image_path in list_non_null_images(images_dir):
            label_path = labels_dir / f"{image_path.stem}.txt"
            if not label_path.is_file():
                print(
                    f"Warning: skip non-NULL image (missing label): {image_path}",
                    file=sys.stderr,
                )
                stats["non_null_missing_label"] += 1
                continue
            non_null_jobs.append((image_path, label_path, source_split))

    if non_null_jobs:
        from ultralytics import YOLO

        model = YOLO(str(weights))
        top_class_id, other_class_id = resolve_top_other_class_ids(model.names)
        job_by_image = {job[0]: job for job in non_null_jobs}

        for batch in chunked([job[0] for job in non_null_jobs], PREDICT_BATCH):
            results = model.predict(
                source=[str(p) for p in batch],
                conf=args.confidence,
                verbose=False,
                device=args.device,
            )
            for image_path, result in zip(batch, results):
                image_path_j, label_path, source_split = job_by_image[image_path]
                boxes = result.boxes
                if boxes is None or len(boxes) == 0:
                    stats["non_null_skipped_low_conf"] += 1
                    continue

                confidence_tensor = boxes.conf
                class_tensor = boxes.cls
                best_index = int(confidence_tensor.argmax().item())
                predicted_class_id = int(class_tensor[best_index].item())

                destination_subfolder = destination_for_prediction(
                    source_split,
                    predicted_class_id,
                    top_class_id,
                    other_class_id,
                )
                register_collision(registry, destination_subfolder, image_path_j, collision_count)
                out_img_dir = output / "images" / destination_subfolder
                out_lbl_dir = output / "labels" / destination_subfolder
                copy_pair(
                    image_path_j,
                    label_path,
                    out_img_dir / image_path_j.name,
                    out_lbl_dir / f"{image_path_j.stem}.txt",
                    args.dry_run,
                )
                stats["non_null_routed"] += 1
                stats[f"dest_{destination_subfolder}"] += 1

    print("Summary:")
    for key in (
        "null_copied",
        "null_missing_label",
        "non_null_missing_label",
        "non_null_routed",
        "non_null_skipped_low_conf",
    ):
        print(f"  {key}: {stats[key]}")
    dest_keys = sorted(k for k in stats if k.startswith("dest_"))
    if dest_keys:
        print("  per_destination_folder:")
        for key in dest_keys:
            print(f"    {key.removeprefix('dest_')}: {stats[key]}")
    print(f"  output_collisions: {collision_count[0]}")
    if args.dry_run:
        print("Dry run: no files were written.")


if __name__ == "__main__":
    main()
