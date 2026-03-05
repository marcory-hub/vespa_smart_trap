#!/usr/bin/env python3
"""
Fill dataset_vespa_2026-02v4_train_val_test_yolo train/valid/test from
dataset_vespa_2026-02v4_train_val_test_yolo/images (jpg) and matching labels
from dataset_vespa_2026-02v4_merge_yolo_cvat_format/obj_train_data (.txt).
Split 85% train, 14% valid, 1% (same logic as v3). Seed 42 for reproducibility.
"""
import random
import shutil
from pathlib import Path

WORKSPACE = Path("/Users/md/Developer/vespa_smart_trap")
SEED = 42
TRAIN_RATIO = 0.85
VALID_RATIO = 0.14
TEST_RATIO = 0.01

IMAGES_DIR = WORKSPACE / "dataset_vespa_2026-02v4_train_val_test_yolo" / "images"
LABELS_DIR = WORKSPACE / "dataset_vespa_2026-02v4_merge_yolo_cvat_format" / "obj_train_data"
TARGET_ROOT = WORKSPACE / "dataset_vespa_2026-02v4_train_val_test_yolo"


def main() -> None:
    if not IMAGES_DIR.exists():
        print(f"Missing: {IMAGES_DIR}")
        return
    if not LABELS_DIR.exists():
        print(f"Missing: {LABELS_DIR}")
        return
    # Remove any files from earlier runs to avoid data leak (only @images split should remain).
    for split_name in ("train", "valid", "test"):
        for sub in ("images", "labels"):
            folder = TARGET_ROOT / split_name / sub
            if folder.exists():
                for f in folder.iterdir():
                    if f.is_file():
                        f.unlink()
    pairs = []
    for img_path in IMAGES_DIR.glob("*.jpg"):
        label_path = LABELS_DIR / (img_path.stem + ".txt")
        if label_path.exists():
            pairs.append((img_path, label_path))
    if not pairs:
        print("No image+label pairs found.")
        return
    random.seed(SEED)
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
        img_dst = TARGET_ROOT / split_name / "images"
        lbl_dst = TARGET_ROOT / split_name / "labels"
        img_dst.mkdir(parents=True, exist_ok=True)
        lbl_dst.mkdir(parents=True, exist_ok=True)
        for img_path, lbl_path in split_pairs:
            shutil.copy2(img_path, img_dst / img_path.name)
            shutil.copy2(lbl_path, lbl_dst / lbl_path.name)
    print(f"v4: {n} pairs -> train={n_train} valid={n_valid} test={n_test}")


if __name__ == "__main__":
    main()
