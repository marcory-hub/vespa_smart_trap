#!/usr/bin/env python3
"""
Split JPG + matching TXT (YOLO labels) into train 85%, valid 14%, test 1%.
Creates train/images, train/labels, valid/images, valid/labels, test/images, test/labels
in each target dataset folder. Uses fixed seed for reproducibility.
"""
import os
import random
import shutil
from pathlib import Path

WORKSPACE = Path("/Users/md/Developer/vespa_smart_trap")
SEED = 42
TRAIN_RATIO = 0.85
VALID_RATIO = 0.14
TEST_RATIO = 0.01

# (source_images_dir, source_labels_dir or None if same as images)
# v3: merged_yolo26 has images/ and labels/. v4: images in train_val_test_yolo/images, labels in obj_train_data.
SOURCES = [
    (
        WORKSPACE / "dataset_vespa_2026-02v3_merged_yolo26" / "images",
        WORKSPACE / "dataset_vespa_2026-02v3_merged_yolo26" / "labels",
    ),
    (
        WORKSPACE / "dataset_vespa_2026-02v4_train_val_test_yolo" / "images",
        WORKSPACE / "dataset_vespa_2026-02v4_merge_yolo_cvat_format" / "obj_train_data",
    ),
]
TARGETS = [
    WORKSPACE / "dataset_vespa_2026-02v3_train_val_test_yolo",
    WORKSPACE / "dataset_vespa_2026-02v4_train_val_test_yolo",
]


def collect_pairs(images_dir: Path, labels_dir: Path | None) -> list[tuple[Path, Path]]:
    """Collect (image_path, label_path) for each jpg that has a matching txt."""
    if labels_dir is None:
        labels_dir = images_dir
    pairs = []
    for img_path in images_dir.glob("*.jpg"):
        label_path = labels_dir / (img_path.stem + ".txt")
        if label_path.exists():
            pairs.append((img_path, label_path))
    return pairs


def main() -> None:
    random.seed(SEED)
    for (images_dir, labels_dir), target_root in zip(SOURCES, TARGETS):
        if not images_dir.exists():
            print(f"Skip (missing source): {images_dir}")
            continue
        pairs = collect_pairs(images_dir, labels_dir)
        if not pairs:
            print(f"Skip (no pairs): {images_dir}")
            continue
        random.shuffle(pairs)
        n = len(pairs)
        n_train = int(round(n * TRAIN_RATIO))
        n_valid = int(round(n * VALID_RATIO))
        n_test = n - n_train - n_valid
        if n_test < 0:
            n_test = 0
            n_valid = n - n_train
        splits = {
            "train": pairs[:n_train],
            "valid": pairs[n_train : n_train + n_valid],
            "test": pairs[n_train + n_valid :],
        }
        for split_name, split_pairs in splits.items():
            img_dst = target_root / split_name / "images"
            lbl_dst = target_root / split_name / "labels"
            img_dst.mkdir(parents=True, exist_ok=True)
            lbl_dst.mkdir(parents=True, exist_ok=True)
            for img_path, lbl_path in split_pairs:
                shutil.copy2(img_path, img_dst / img_path.name)
                shutil.copy2(lbl_path, lbl_dst / lbl_path.name)
        print(f"{target_root.name}: {n} pairs -> train={n_train} valid={n_valid} test={n_test}")


if __name__ == "__main__":
    main()
