#!/usr/bin/env python3
"""
Match merged label files to existing split images and copy to split label folders.

Reads image filenames from dataset/test/images/, dataset/train/images/, and
dataset/valid/images/, then matches them with labels from
original.vXi.yolo26/labels.vXi.yolo26/ and copies matching label files to
dataset/test/labels/, dataset/train/labels/, and dataset/valid/labels/.

Auto-detects v3 vs v4 from dataset root path.
Reusable for both v3 and v4 datasets.
"""
import argparse
import shutil
import sys
from pathlib import Path

SPLITS = ["test", "train", "valid"]


def match_labels_to_split(
    images_dir: Path,
    labels_source_dir: Path,
    labels_target_dir: Path,
    split_name: str,
) -> tuple[int, int]:
    """
    Match label files to images in a split folder and copy them.

    Args:
        images_dir: Directory containing split images
        labels_source_dir: Directory containing merged label files
        labels_target_dir: Target directory for matched label files
        split_name: Name of the split (for logging)

    Returns:
        Tuple of (labels_matched, images_without_labels)
    """
    if not images_dir.exists():
        print(f"Warning: Images directory does not exist: {images_dir}")
        return 0, 0

    labels_target_dir.mkdir(parents=True, exist_ok=True)

    # Find all image files
    image_files = (
        list(images_dir.glob("*.jpg"))
        + list(images_dir.glob("*.jpeg"))
        + list(images_dir.glob("*.png"))
    )

    if not image_files:
        print(f"Warning: No images found in {images_dir}")
        return 0, 0

    labels_matched = 0
    images_without_labels = 0
    missing_labels = []

    total_images = len(image_files)
    print(f"  Processing {split_name}: {total_images} images...", end="", flush=True)

    for idx, image_file in enumerate(image_files, 1):
        # Get stem (filename without extension) to match with label file
        stem = image_file.stem
        label_filename = f"{stem}.txt"
        source_label = labels_source_dir / label_filename
        target_label = labels_target_dir / label_filename

        if source_label.exists():
            # Copy label file to target directory
            shutil.copy2(source_label, target_label)
            labels_matched += 1
        else:
            images_without_labels += 1
            missing_labels.append(image_file.name)

        # Progress indicator every 100 files
        if idx % 100 == 0 or idx == total_images:
            print(f" {idx}/{total_images}", end="", flush=True)

    print(f" ✓ ({labels_matched} matched, {images_without_labels} missing)")

    if missing_labels:
        print(f"  Warning: {split_name} - {len(missing_labels)} images without matching labels:")
        # Print first 10 missing labels as examples
        for img_name in missing_labels[:10]:
            print(f"    - {img_name}")
        if len(missing_labels) > 10:
            print(f"    ... and {len(missing_labels) - 10} more")

    return labels_matched, images_without_labels


def detect_version(dataset_root: Path) -> str:
    """
    Detect dataset version (v3 or v4) from dataset root path and return version suffix.

    Args:
        dataset_root: Path to dataset root directory

    Returns:
        Version suffix string: "v3i.yolo26" or "v4i.yolo26"
    """
    dataset_name = dataset_root.name

    # Check for v3 in path (e.g., dataset_vespa_2026-02v3_train_val_test_yolo)
    if "v3" in dataset_name and "v4" not in dataset_name:
        return "v3i.yolo26"
    # Check for v4 in path (e.g., dataset_vespa_2026-02v4_train_val_test_yolo)
    elif "v4" in dataset_name:
        return "v4i.yolo26"
    else:
        # Try to detect by checking which original directory exists
        v3_dir = dataset_root / "original.v3i.yolo26"
        v4_dir = dataset_root / "original.v4i.yolo26"
        if v3_dir.exists() and not v4_dir.exists():
            return "v3i.yolo26"
        elif v4_dir.exists() and not v3_dir.exists():
            return "v4i.yolo26"
        else:
            # Default to v4 if ambiguous
            print("Warning: Could not detect version from path, defaulting to v4")
            return "v4i.yolo26"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Match merged label files to existing split images and copy to split label folders."
    )
    parser.add_argument(
        "--dataset-root",
        type=str,
        required=True,
        help="Root path of the dataset (e.g., dataset_vespa_2026-02v4_train_val_test_yolo)",
    )
    args = parser.parse_args()

    dataset_root = Path(args.dataset_root).resolve()
    if not dataset_root.exists():
        print(f"Error: Dataset root directory does not exist: {dataset_root}")
        sys.exit(1)

    # Detect version and construct labels source directory path
    version_suffix = detect_version(dataset_root)
    labels_source_dir = dataset_root / f"original.{version_suffix}" / f"labels.{version_suffix}"

    if not labels_source_dir.exists():
        print(f"Error: Merged labels directory does not exist: {labels_source_dir}")
        print(f"Detected version suffix: {version_suffix}")
        print("Hint: Run merge_original_class_folders.py first to create merged labels.")
        sys.exit(1)

    print(f"Detected version: {version_suffix}")

    dataset_dir = dataset_root / "dataset"
    if not dataset_dir.exists():
        print(f"Error: Dataset directory does not exist: {dataset_dir}")
        sys.exit(1)

    total_labels_matched = 0
    total_images_without_labels = 0

    print(f"\nMatching labels from: {labels_source_dir}")
    print(f"To split folders in: {dataset_dir}\n")

    # Process each split
    for split_name in SPLITS:
        images_dir = dataset_dir / split_name / "images"
        labels_target_dir = dataset_dir / split_name / "labels"

        labels_matched, images_without_labels = match_labels_to_split(
            images_dir,
            labels_source_dir,
            labels_target_dir,
            split_name,
        )

        total_labels_matched += labels_matched
        total_images_without_labels += images_without_labels

    print(f"\nDone. Total: {total_labels_matched} labels matched, {total_images_without_labels} images without labels.")


if __name__ == "__main__":
    main()
