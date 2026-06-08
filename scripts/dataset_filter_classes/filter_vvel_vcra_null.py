#!/usr/bin/env python3
"""
Keep vvel, vcra, and NULL; drop amel and vespsp from YOLO dataset folders.

Removes amel and vespsp image/label pairs (classes 0 and 2).
Rewrites kept label files: strips any remaining amel/vespsp boxes, remaps
vcra 1->0 and vvel 3->1. Deletes vvel/vcra pairs that end up with no boxes.
Updates data.yaml to nc: 2 and names: [vcra, vvel].

Targets:
  data/dataset_images_labels   (images/{split}/ + labels/{split}/)
  data/dataset_test_train_val  ({split}/images/ + {split}/labels/)

Dry-run by default; use --apply to delete files and rewrite labels/yaml.

Usage:
  source .venv/bin/activate
  python3 scripts/dataset_filter_classes/filter_vvel_vcra_null.py
  python3 scripts/dataset_filter_classes/filter_vvel_vcra_null.py --apply
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

KEPT_CLASS_PREFIXES = frozenset({"vvel", "vcra", "NULL"})
DROPPED_CLASS_PREFIXES = frozenset({"amel", "vespsp"})  # classes 0, 2
DROPPED_CLASS_IDS = frozenset({"0", "2"})  # amel, vespsp
OLD_TO_NEW_CLASS = {"1": "0", "3": "1"}  # vcra, vvel
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}

SPLITS = ("train", "val", "test")

PREFIX_PATTERN = re.compile(r"^([a-zA-Z]+)")


@dataclass
class SplitStats:
    removed_dropped_classes: int = 0
    removed_empty_after_filter: int = 0
    labels_rewritten: int = 0
    labels_unchanged: int = 0
    images_removed: int = 0
    orphan_images_removed: int = 0
    removed_dropped_class_examples: list[str] = field(default_factory=list)


@dataclass
class DatasetStats:
    dataset_root: Path
    splits: dict[str, SplitStats] = field(default_factory=dict)


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(
        description="Drop amel and vespsp; keep vvel, vcra, and NULL."
    )
    parser.add_argument(
        "--dataset-images-labels",
        type=Path,
        default=project_root / "data/dataset_images_labels",
        help="Flat images/ + labels/ split layout.",
    )
    parser.add_argument(
        "--dataset-test-train-val",
        type=Path,
        default=project_root / "data/dataset_test_train_val",
        help="YOLO {split}/images + {split}/labels layout.",
    )
    parser.add_argument(
        "--skip-images-labels",
        action="store_true",
        help="Do not process dataset_images_labels.",
    )
    parser.add_argument(
        "--skip-test-train-val",
        action="store_true",
        help="Do not process dataset_test_train_val.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Delete files and rewrite labels/yaml (default is dry-run).",
    )
    return parser.parse_args()


def filename_prefix(stem: str) -> str:
    if stem.startswith("NULL"):
        return "NULL"
    match = PREFIX_PATTERN.match(stem)
    return match.group(1) if match else ""


def find_image(images_dir: Path, stem: str) -> Path | None:
    for suffix in IMAGE_SUFFIXES:
        candidate = images_dir / f"{stem}{suffix}"
        if candidate.is_file():
            return candidate
    return None


def rewrite_label_lines(content: str) -> list[str]:
    kept_lines: list[str] = []
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split()
        class_id = parts[0]
        if class_id in DROPPED_CLASS_IDS:
            continue
        if class_id not in OLD_TO_NEW_CLASS:
            raise ValueError(f"Unexpected class id {class_id!r} in line: {line}")
        parts[0] = OLD_TO_NEW_CLASS[class_id]
        kept_lines.append(" ".join(parts))
    return kept_lines


def remove_path(path: Path, apply: bool) -> None:
    if apply and path.is_file():
        path.unlink()


def label_needs_rewrite(original: str) -> bool:
    for raw_line in original.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        class_id = line.split()[0]
        if class_id in DROPPED_CLASS_IDS:
            return True
        if OLD_TO_NEW_CLASS.get(class_id, class_id) != class_id:
            return True
    return False


def process_split(
    labels_dir: Path,
    images_dir: Path,
    apply: bool,
    max_examples: int = 5,
) -> SplitStats:
    stats = SplitStats()
    if not labels_dir.is_dir():
        return stats
    if not images_dir.is_dir():
        print(f"WARNING: images dir missing: {images_dir}", file=sys.stderr)
        return stats

    label_paths = sorted(
        path for path in labels_dir.iterdir() if path.is_file() and path.suffix == ".txt"
    )
    seen_image_stems: set[str] = set()

    for label_path in label_paths:
        stem = label_path.stem
        prefix = filename_prefix(stem)
        image_path = find_image(images_dir, stem)
        if image_path is not None:
            seen_image_stems.add(stem)

        if prefix in DROPPED_CLASS_PREFIXES:
            stats.removed_dropped_classes += 1
            if len(stats.removed_dropped_class_examples) < max_examples:
                stats.removed_dropped_class_examples.append(label_path.name)
            remove_path(label_path, apply)
            if image_path is not None:
                remove_path(image_path, apply)
                stats.images_removed += 1
            continue

        original = label_path.read_text(encoding="utf-8")
        new_lines = rewrite_label_lines(original)

        if not new_lines and prefix != "NULL":
            stats.removed_empty_after_filter += 1
            remove_path(label_path, apply)
            if image_path is not None:
                remove_path(image_path, apply)
                stats.images_removed += 1
            continue

        new_content = "\n".join(new_lines)
        if new_lines:
            new_content += "\n"

        if label_needs_rewrite(original):
            stats.labels_rewritten += 1
            if apply and new_content != original:
                label_path.write_text(new_content, encoding="utf-8")
        else:
            stats.labels_unchanged += 1

    for image_path in sorted(images_dir.iterdir()):
        if not image_path.is_file():
            continue
        if image_path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        stem = image_path.stem
        if stem in seen_image_stems:
            continue
        prefix = filename_prefix(stem)
        if prefix in DROPPED_CLASS_PREFIXES:
            stats.orphan_images_removed += 1
            remove_path(image_path, apply)

    return stats


def split_dirs_flat(dataset_root: Path, split: str) -> tuple[Path, Path]:
    return dataset_root / "labels" / split, dataset_root / "images" / split


def split_dirs_nested(dataset_root: Path, split: str) -> tuple[Path, Path]:
    return dataset_root / split / "labels", dataset_root / split / "images"


def process_dataset(
    dataset_root: Path,
    layout: str,
    apply: bool,
) -> DatasetStats:
    result = DatasetStats(dataset_root=dataset_root)
    for split in SPLITS:
        if layout == "flat":
            labels_dir, images_dir = split_dirs_flat(dataset_root, split)
        else:
            labels_dir, images_dir = split_dirs_nested(dataset_root, split)
        if not labels_dir.is_dir() and not images_dir.is_dir():
            continue
        result.splits[split] = process_split(labels_dir, images_dir, apply)
    return result


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def update_data_yaml(path: Path, apply: bool) -> dict:
    data = load_yaml(path)
    data["nc"] = 2
    data["names"] = ["vcra", "vvel"]
    if apply:
        with path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(data, handle, sort_keys=False, default_flow_style=False)
    return data


def print_split_stats(split: str, stats: SplitStats) -> None:
    print(f"  [{split}]")
    print(f"    removed (amel/vespsp):    {stats.removed_dropped_classes}")
    print(f"    removed (empty labels):   {stats.removed_empty_after_filter}")
    print(f"    labels rewritten:         {stats.labels_rewritten}")
    print(f"    labels unchanged:         {stats.labels_unchanged}")
    print(f"    images removed w/ labels: {stats.images_removed}")
    print(f"    orphan images removed:    {stats.orphan_images_removed}")
    if stats.removed_dropped_class_examples:
        print(f"    dropped class examples:   {', '.join(stats.removed_dropped_class_examples)}")


def print_dataset_stats(title: str, stats: DatasetStats) -> None:
    print(title)
    print(f"  root: {stats.dataset_root}")
    if not stats.splits:
        print("  (no split folders found)")
        return
    for split, split_stats in stats.splits.items():
        print_split_stats(split, split_stats)


def main() -> int:
    args = parse_args()
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"Mode: {mode}\n")

    all_stats: list[tuple[str, DatasetStats]] = []

    if not args.skip_images_labels:
        root = args.dataset_images_labels.expanduser().resolve()
        if root.is_dir():
            stats = process_dataset(root, layout="flat", apply=args.apply)
            all_stats.append(("dataset_images_labels", stats))
            yaml_path = root / "data.yaml"
            if yaml_path.is_file():
                updated = update_data_yaml(yaml_path, apply=args.apply)
                print(f"data.yaml ({yaml_path}):")
                print(f"  nc: {updated.get('nc')}, names: {updated.get('names')}")
                print()
        else:
            print(f"SKIP: not found: {root}\n")

    if not args.skip_test_train_val:
        root = args.dataset_test_train_val.expanduser().resolve()
        if root.is_dir():
            stats = process_dataset(root, layout="nested", apply=args.apply)
            all_stats.append(("dataset_test_train_val", stats))
            yaml_path = root / "data.yaml"
            if yaml_path.is_file():
                updated = update_data_yaml(yaml_path, apply=args.apply)
                print(f"data.yaml ({yaml_path}):")
                print(f"  nc: {updated.get('nc')}, names: {updated.get('names')}")
                print()
        else:
            print(f"SKIP: not found: {root}\n")

    for title, stats in all_stats:
        print_dataset_stats(title, stats)
        print()

    if not args.apply:
        print("Re-run with --apply to delete files and write label/yaml changes.")
        print("WARNING: Irreversible operation. Data loss/Overwrite risk.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
