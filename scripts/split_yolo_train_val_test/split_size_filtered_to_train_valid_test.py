#!/usr/bin/env python3
"""
Split each size-filtered merged folder into train (85%), valid (14%), test (1%).

Reads from flat dataset_vespa/merged_30px/images and merged_30px/labels (and 40px, 60px).
Writes to final dataset folders at workspace root with train/images, train/labels,
valid/images, valid/labels, test/images, test/labels. Filenames preserved.
Exits if target dataset dirs already have content unless --overwrite.
"""
import argparse
import random
import shutil
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
# Read from dataset_vespa/merged_* ; write final datasets at workspace root
SOURCE_ROOT = WORKSPACE / "dataset_vespa"
SEED = 42
TRAIN_RATIO = 0.85
VALID_RATIO = 0.14
TEST_RATIO = 0.01
SPLITS = ("train", "valid", "test")

# merged folder name (under dataset_vespa) -> final dataset folder name (at workspace root)
MERGED_TO_TARGET = [
    ("merged_30px", "dataset_vespa_2026-02v1_30px_nopre_aug_train_valid_test_yolo"),
    ("merged_40px", "dataset_vespa_2026-02v1_40px_nopre_aug_train_valid_test_yolo"),
    ("merged_60px", "dataset_vespa_2026-02v1_60px_nopre_aug_train_valid_test_yolo"),
]
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


def collect_pairs(merged_name: str) -> list[tuple[Path, Path]]:
    """Collect (image_path, label_path) from flat merged_*/images and merged_*/labels."""
    pairs = []
    images_dir = SOURCE_ROOT / merged_name / "images"
    labels_dir = SOURCE_ROOT / merged_name / "labels"
    if not images_dir.is_dir():
        return pairs
    for ext in IMAGE_EXTENSIONS:
        for img_path in images_dir.glob(f"*{ext}"):
            if not img_path.is_file():
                continue
            label_path = labels_dir / (img_path.stem + ".txt")
            if label_path.exists():
                pairs.append((img_path, label_path))
    return pairs


def target_has_content(target_root: Path) -> bool:
    """True if any train/valid/test images or labels subdir has files."""
    for split_name in SPLITS:
        img_dir = target_root / split_name / "images"
        if img_dir.is_dir() and any(img_dir.iterdir()):
            return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Split merged_* into train/valid/test; preserve filenames.")
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting existing target dataset content.")
    args = parser.parse_args()

    random.seed(SEED)
    for merged_name, target_name in MERGED_TO_TARGET:
        target_root = WORKSPACE / target_name
        if target_has_content(target_root) and not args.overwrite:
            print(f"Skip {merged_name}: {target_name} already has content. Use --overwrite to replace.")
            continue
        pairs = collect_pairs(merged_name)
        if not pairs:
            print(f"Skip {merged_name}: no image+label pairs")
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
        print(f"{target_name}: {n} pairs -> train={n_train} valid={n_valid} test={n_test}")


if __name__ == "__main__":
    main()
