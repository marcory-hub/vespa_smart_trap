#!/usr/bin/env python3
"""
Backfill missing top-view label files in cv_vespa_2026-05_top_images_labels.

For each image in images/{test,train,val}/ without a matching label in
labels/{test_top,train_top,val_top}/, copy the label from the canonical
fallback folder data/dataset_top/labels/train/ when available.

Usage:
  source .venv/bin/activate
  python3 scripts/dataset_top_copy/backfill_missing_top_labels.py --dry-run
  python3 scripts/dataset_top_copy/backfill_missing_top_labels.py
"""

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}

SPLIT_MAPPINGS: tuple[tuple[str, str], ...] = (
    ("test", "test_top"),
    ("train", "train_top"),
    ("val", "val_top"),
)


@dataclass
class BackfillStats:
    labels_copied: int = 0
    labels_skipped_existing: int = 0
    labels_not_found: int = 0
    missing_names: list[str] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[2]
    default_source = project_root / "data/dataset_top/cv_vespa_2026-05_top_images_labels"
    default_fallback = project_root / "data/dataset_top/labels/train"

    parser = argparse.ArgumentParser(
        description="Backfill missing top-view labels from dataset_top/labels/train."
    )
    parser.add_argument("--source", type=Path, default=default_source)
    parser.add_argument("--fallback-labels", type=Path, default=default_fallback)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def list_images(image_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in image_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )


def backfill_split(
    source_root: Path,
    fallback_labels_dir: Path,
    split_name: str,
    label_split_name: str,
    *,
    dry_run: bool,
    overwrite: bool,
) -> BackfillStats:
    stats = BackfillStats()
    image_dir = source_root / "images" / split_name
    label_dir = source_root / "labels" / label_split_name
    label_dir.mkdir(parents=True, exist_ok=True)

    for image_path in list_images(image_dir):
        destination_label = label_dir / f"{image_path.stem}.txt"
        if destination_label.is_file() and not overwrite:
            continue

        fallback_label = fallback_labels_dir / f"{image_path.stem}.txt"
        if not fallback_label.is_file():
            stats.labels_not_found += 1
            stats.missing_names.append(image_path.name)
            continue

        if dry_run:
            action = "replace" if destination_label.exists() else "copy"
            print(
                f"[dry-run] would {action}: {fallback_label} -> {destination_label}"
            )
            stats.labels_copied += 1
            continue

        shutil.copy2(fallback_label, destination_label)
        stats.labels_copied += 1

    return stats


def main() -> int:
    args = parse_args()
    source_root = args.source.resolve()
    fallback_labels_dir = args.fallback_labels.resolve()

    if not source_root.is_dir():
        print(f"Source directory not found: {source_root}", file=sys.stderr)
        return 1
    if not fallback_labels_dir.is_dir():
        print(f"Fallback label directory not found: {fallback_labels_dir}", file=sys.stderr)
        return 1

    print(f"Source:           {source_root}")
    print(f"Fallback labels:  {fallback_labels_dir}")
    print(f"Dry run:          {args.dry_run}")

    all_stats: dict[str, BackfillStats] = {}
    for split_name, label_split_name in SPLIT_MAPPINGS:
        all_stats[split_name] = backfill_split(
            source_root,
            fallback_labels_dir,
            split_name,
            label_split_name,
            dry_run=args.dry_run,
            overwrite=args.overwrite,
        )

    print("\nSummary")
    print("-------")
    for split_name, stats in all_stats.items():
        print(f"{split_name}: copied={stats.labels_copied} not_found={stats.labels_not_found}")

    total_not_found = sum(stats.labels_not_found for stats in all_stats.values())
    if total_not_found:
        print(f"\nWarning: {total_not_found} image(s) still have no fallback label.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
