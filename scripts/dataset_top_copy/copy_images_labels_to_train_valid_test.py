#!/usr/bin/env python3
"""
Copy split images and labels into YOLO train/valid/test layout.

Source layout (cv_vespa_2026-05_top_images_labels):
  images/{test,train,val}/
  labels/{test_top,train_top,val_top}/

Destination layout (cv_vespa_2026-05-top_train_valid_test):
  {test,train,val}/images/
  {test,train,val}/labels/

By default, only image/label pairs with matching stems are copied.
Images without a matching .txt label are skipped and reported.

Workflow:
  1. Backfill any missing labels in the source folder:
     python3 scripts/dataset_top_copy/backfill_missing_top_labels.py --dry-run
  2. Copy paired files into the YOLO layout:
     python3 scripts/dataset_top_copy/copy_images_labels_to_train_valid_test.py --dry-run

Usage:
  source .venv/bin/activate
  python3 scripts/dataset_top_copy/copy_images_labels_to_train_valid_test.py --dry-run
  python3 scripts/dataset_top_copy/copy_images_labels_to_train_valid_test.py
"""

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}

SPLIT_MAPPINGS: tuple[tuple[str, str, str], ...] = (
    ("test", "test", "test_top"),
    ("train", "train", "train_top"),
    ("val", "val", "val_top"),
)


@dataclass
class SplitStats:
    images_copied: int = 0
    labels_copied: int = 0
    images_skipped_unlabeled: int = 0
    images_skipped_existing: int = 0
    labels_skipped_existing: int = 0
    unlabeled_image_names: list[str] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[2]
    default_source = project_root / "data/dataset_top/cv_vespa_2026-05_top_images_labels"
    default_destination = project_root / "data/dataset_top/cv_vespa_2026-05-top_train_valid_test"

    parser = argparse.ArgumentParser(
        description=(
            "Copy split images and labels from the top-view source folder "
            "into the YOLO train/val/test destination folder."
        )
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=default_source,
        help=f"Source dataset root (default: {default_source})",
    )
    parser.add_argument(
        "--destination",
        type=Path,
        default=default_destination,
        help=f"Destination dataset root (default: {default_destination})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned copies without writing files.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace files that already exist in the destination.",
    )
    parser.add_argument(
        "--include-unlabeled",
        action="store_true",
        help="Copy images even when no matching .txt label exists.",
    )
    return parser.parse_args()


def list_images(image_dir: Path) -> list[Path]:
    if not image_dir.is_dir():
        raise FileNotFoundError(f"Missing image directory: {image_dir}")

    images = [
        path
        for path in sorted(image_dir.iterdir())
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    ]
    return images


def label_path_for_image(label_dir: Path, image_path: Path) -> Path:
    return label_dir / f"{image_path.stem}.txt"


def copy_file(source: Path, destination: Path, *, dry_run: bool, overwrite: bool) -> bool:
    if destination.exists() and not overwrite:
        return False

    if dry_run:
        action = "replace" if destination.exists() else "copy"
        print(f"[dry-run] would {action}: {source} -> {destination}")
        return True

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return True


def copy_split(
    source_root: Path,
    destination_root: Path,
    split_name: str,
    source_image_split: str,
    source_label_split: str,
    *,
    dry_run: bool,
    overwrite: bool,
    include_unlabeled: bool,
) -> SplitStats:
    stats = SplitStats()
    source_images_dir = source_root / "images" / source_image_split
    source_labels_dir = source_root / "labels" / source_label_split
    destination_images_dir = destination_root / split_name / "images"
    destination_labels_dir = destination_root / split_name / "labels"

    if not source_labels_dir.is_dir():
        raise FileNotFoundError(f"Missing label directory: {source_labels_dir}")

    for image_path in list_images(source_images_dir):
        label_path = label_path_for_image(source_labels_dir, image_path)
        has_label = label_path.is_file()

        if not has_label and not include_unlabeled:
            stats.images_skipped_unlabeled += 1
            stats.unlabeled_image_names.append(image_path.name)
            continue

        destination_image = destination_images_dir / image_path.name
        if copy_file(image_path, destination_image, dry_run=dry_run, overwrite=overwrite):
            stats.images_copied += 1
        else:
            stats.images_skipped_existing += 1

        if has_label:
            destination_label = destination_labels_dir / label_path.name
            if copy_file(label_path, destination_label, dry_run=dry_run, overwrite=overwrite):
                stats.labels_copied += 1
            else:
                stats.labels_skipped_existing += 1

    return stats


def print_split_summary(split_name: str, stats: SplitStats) -> None:
    print(f"\n{split_name}:")
    print(f"  images copied:              {stats.images_copied}")
    print(f"  labels copied:              {stats.labels_copied}")
    print(f"  images skipped (unlabeled): {stats.images_skipped_unlabeled}")
    print(f"  images skipped (existing):  {stats.images_skipped_existing}")
    print(f"  labels skipped (existing):  {stats.labels_skipped_existing}")

    if stats.unlabeled_image_names:
        preview = ", ".join(stats.unlabeled_image_names[:5])
        suffix = " ..." if len(stats.unlabeled_image_names) > 5 else ""
        print(f"  unlabeled examples:         {preview}{suffix}")


def main() -> int:
    args = parse_args()
    source_root = args.source.resolve()
    destination_root = args.destination.resolve()

    if not source_root.is_dir():
        print(f"Source directory not found: {source_root}", file=sys.stderr)
        return 1

    destination_root.mkdir(parents=True, exist_ok=True)

    print(f"Source:      {source_root}")
    print(f"Destination: {destination_root}")
    print(f"Dry run:     {args.dry_run}")
    print(f"Overwrite:   {args.overwrite}")
    print(f"Unlabeled:   {'include' if args.include_unlabeled else 'skip'}")

    all_stats: dict[str, SplitStats] = {}

    try:
        for split_name, source_image_split, source_label_split in SPLIT_MAPPINGS:
            all_stats[split_name] = copy_split(
                source_root,
                destination_root,
                split_name,
                source_image_split,
                source_label_split,
                dry_run=args.dry_run,
                overwrite=args.overwrite,
                include_unlabeled=args.include_unlabeled,
            )
    except FileNotFoundError as error:
        print(error, file=sys.stderr)
        return 1

    print("\nSummary")
    print("-------")
    for split_name, stats in all_stats.items():
        print_split_summary(split_name, stats)

    total_unlabeled = sum(stats.images_skipped_unlabeled for stats in all_stats.values())
    if total_unlabeled:
        print(
            f"\nNote: {total_unlabeled} image(s) had no matching label and were skipped. "
            "Use --include-unlabeled to copy them anyway."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
