#!/usr/bin/env python3
"""
Copy matching labels into dataset split label folders for dataset_vespa_2026-02v3_merged_yolo.

Reads image filenames from dataset_vespa_2026-02v3_merged_yolo/dataset/{test,train,valid}/images,
matches them with labels from dataset_vespa_2026-02v3_merged_yolo/labels.v3i.yolo26,
and copies matching label files to dataset_vespa_2026-02v3_merged_yolo/dataset/{test,train,valid}/labels.

Original images in images.v3i.yolo26 are not modified.
"""
import shutil
import sys
from pathlib import Path

WORKSPACE = Path("/Users/md/Developer/vespa_smart_trap")
DATASET_ROOT = WORKSPACE / "dataset_vespa_2026-02v3_merged_yolo"
LABELS_SOURCE = DATASET_ROOT / "labels.v3i.yolo26"

SPLITS = ["test", "train", "valid"]


def match_labels_to_split(
    images_dir: Path,
    labels_source_dir: Path,
    labels_target_dir: Path,
    split_name: str,
) -> tuple[int, int]:
    """
    Match label files to images in a split folder and copy them.

    Returns:
        Tuple of (labels_matched, images_without_labels)
    """
    if not images_dir.exists():
        print(f"Warning: Images directory does not exist: {images_dir}")
        return 0, 0

    labels_target_dir.mkdir(parents=True, exist_ok=True)

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
    print(f"  {split_name}: {total_images} images...", end="", flush=True)

    for idx, image_file in enumerate(image_files, 1):
        stem = image_file.stem
        label_filename = f"{stem}.txt"
        source_label = labels_source_dir / label_filename
        target_label = labels_target_dir / label_filename

        if source_label.exists():
            shutil.copy2(source_label, target_label)
            labels_matched += 1
        else:
            images_without_labels += 1
            missing_labels.append(image_file.name)

        if idx % 100 == 0 or idx == total_images:
            print(f" {idx}/{total_images}", end="", flush=True)

    print(f" -> {labels_matched} labels copied, {images_without_labels} missing")

    if missing_labels and len(missing_labels) <= 10:
        for img_name in missing_labels:
            print(f"    - {img_name}")
    elif missing_labels:
        for img_name in missing_labels[:10]:
            print(f"    - {img_name}")
        print(f"    ... and {len(missing_labels) - 10} more")

    return labels_matched, images_without_labels


def main() -> None:
    if not DATASET_ROOT.exists():
        print(f"Error: Dataset root does not exist: {DATASET_ROOT}")
        sys.exit(1)

    if not LABELS_SOURCE.exists():
        print(f"Error: Labels source does not exist: {LABELS_SOURCE}")
        sys.exit(1)

    dataset_dir = DATASET_ROOT / "dataset"
    if not dataset_dir.exists():
        print(f"Error: Dataset directory does not exist: {dataset_dir}")
        sys.exit(1)

    print(f"Labels source: {LABELS_SOURCE}")
    print(f"Target splits: {dataset_dir}\n")

    total_matched = 0
    total_missing = 0

    for split_name in SPLITS:
        images_dir = dataset_dir / split_name / "images"
        labels_target_dir = dataset_dir / split_name / "labels"
        matched, missing = match_labels_to_split(
            images_dir,
            LABELS_SOURCE,
            labels_target_dir,
            split_name,
        )
        total_matched += matched
        total_missing += missing

    print(f"\nDone. Total: {total_matched} labels copied, {total_missing} images without labels.")


if __name__ == "__main__":
    main()
