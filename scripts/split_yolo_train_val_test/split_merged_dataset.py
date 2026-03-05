#!/usr/bin/env python3
"""
Split merged images and labels into train (85%), valid (14%), and test (1%) splits.

Reads images from dataset_vesp_2026-02_per_class_yolo/merged/images and matching labels
from dataset_vesp_2026-02_per_class_yolo/merged/labels, then splits them into
train/valid/test sets with seed=42 for reproducibility.

Creates dataset/train/images, dataset/train/labels, dataset/valid/images,
dataset/valid/labels, dataset/test/images, dataset/test/labels.

Includes images without labels (for NULL background data).
"""
import random
import shutil
from pathlib import Path

WORKSPACE = Path("/Users/md/Developer/vespa_smart_trap")
DATASET_ROOT = WORKSPACE / "dataset_vesp_2026-02_per_class_yolo"
SEED = 42
TRAIN_RATIO = 0.85
VALID_RATIO = 0.14
TEST_RATIO = 0.01

MERGED_IMAGES_DIR = DATASET_ROOT / "merged" / "images"
MERGED_LABELS_DIR = DATASET_ROOT / "merged" / "labels"
TARGET_ROOT = DATASET_ROOT / "dataset"


def collect_image_label_pairs(images_dir: Path, labels_dir: Path) -> list[tuple[Path, Path | None]]:
    """
    Collect (image_path, label_path_or_none) pairs for all images.

    Args:
        images_dir: Directory containing image files
        labels_dir: Directory containing label files

    Returns:
        List of tuples: (image_path, label_path_or_none)
        Includes images without labels (label_path will be None)
    """
    pairs = []
    image_extensions = (".jpg", ".jpeg", ".png")

    for img_path in images_dir.iterdir():
        if img_path.is_file() and img_path.suffix.lower() in image_extensions:
            label_path = labels_dir / (img_path.stem + ".txt")
            if label_path.exists():
                pairs.append((img_path, label_path))
            else:
                # Include images without labels (for NULL background data)
                pairs.append((img_path, None))

    return pairs


def main() -> None:
    if not MERGED_IMAGES_DIR.exists():
        print(f"Error: Merged images directory does not exist: {MERGED_IMAGES_DIR}")
        return

    if not MERGED_LABELS_DIR.exists():
        print(f"Warning: Merged labels directory does not exist: {MERGED_LABELS_DIR}")
        print("Will proceed with images only (no labels)")

    # Collect all image-label pairs
    pairs = collect_image_label_pairs(MERGED_IMAGES_DIR, MERGED_LABELS_DIR)
    if not pairs:
        print("No images found to split.")
        return

    # Set random seed and shuffle
    random.seed(SEED)
    random.shuffle(pairs)

    # Calculate split sizes
    n = len(pairs)
    n_train = int(round(n * TRAIN_RATIO))
    n_valid = int(round(n * VALID_RATIO))
    n_test = n - n_train - n_valid

    # Handle rounding edge cases
    if n_test < 0:
        n_test = 0
        n_valid = n - n_train

    splits = {
        "train": pairs[:n_train],
        "valid": pairs[n_train : n_train + n_valid],
        "test": pairs[n_train + n_valid :],
    }

    # Copy files to split directories
    for split_name, split_pairs in splits.items():
        img_dst = TARGET_ROOT / split_name / "images"
        lbl_dst = TARGET_ROOT / split_name / "labels"
        img_dst.mkdir(parents=True, exist_ok=True)
        lbl_dst.mkdir(parents=True, exist_ok=True)

        for img_path, lbl_path in split_pairs:
            # Copy image
            shutil.copy2(img_path, img_dst / img_path.name)
            # Copy label if it exists
            if lbl_path is not None:
                shutil.copy2(lbl_path, lbl_dst / lbl_path.name)

    print(f"{TARGET_ROOT.name}: {n} pairs -> train={n_train} valid={n_valid} test={n_test}")


if __name__ == "__main__":
    main()
