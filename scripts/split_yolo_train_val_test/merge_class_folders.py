#!/usr/bin/env python3
"""
Merge images and labels from 5 class-specific folders into consolidated folders.

Merges images from dataset_vesp_2026-02_per_class_yolo/{class}.v1i.yolo26/train/images/
into dataset_vesp_2026-02_per_class_yolo/merged/images/, and labels from
dataset_vesp_2026-02_per_class_yolo/{class}.v1i.yolo26/train/labels/ into
dataset_vesp_2026-02_per_class_yolo/merged/labels/.

Class folders: amel.v1i.yolo26, NULL.v1i.yolo26, vcra.v1i.yolo26, vespsp.v1i.yolo26, vvel_1_2_yolo26
NULL folder may have no labels (background data).
"""
import shutil
import sys
from pathlib import Path

WORKSPACE = Path("/Users/md/Developer/vespa_smart_trap")
DATASET_ROOT = WORKSPACE / "dataset_vesp_2026-02_per_class_yolo"

CLASS_FOLDERS = [
    "amel.v1i.yolo26",
    "NULL.v1i.yolo26",
    "vcra.v1i.yolo26",
    "vespsp.v1i.yolo26",
    "vvel_1_2_yolo26",
]


def merge_files(
    source_dirs: list[Path],
    target_dir: Path,
    file_type: str,
) -> int:
    """
    Merge files from multiple source directories into a target directory.

    Args:
        source_dirs: List of source directories to merge from
        target_dir: Target directory to merge into
        file_type: Description of file type for logging ("images" or "labels")

    Returns:
        Number of files copied
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    files_copied = 0

    for source_dir in source_dirs:
        if not source_dir.exists():
            print(f"Warning: Source directory does not exist: {source_dir}")
            continue

        # Find all files in source directory
        if file_type == "images":
            files = list(source_dir.glob("*.jpg")) + list(source_dir.glob("*.jpeg")) + list(source_dir.glob("*.png"))
        else:  # labels
            files = list(source_dir.glob("*.txt"))

        total_files = len(files)
        if total_files == 0:
            print(f"  {source_dir.parent.name}: No {file_type} found")
            continue

        print(f"  Processing {source_dir.parent.name}: {total_files} {file_type}...", end="", flush=True)

        for idx, source_file in enumerate(files, 1):
            filename = source_file.name
            target_file = target_dir / filename

            # Copy file
            shutil.copy2(source_file, target_file)
            files_copied += 1

            # Progress indicator every 100 files
            if idx % 100 == 0 or idx == total_files:
                print(f" {idx}/{total_files}", end="", flush=True)

        print(f" ✓ ({files_copied} total copied so far)")

    return files_copied


def main() -> None:
    if not DATASET_ROOT.exists():
        print(f"Error: Dataset root directory does not exist: {DATASET_ROOT}")
        sys.exit(1)

    # Prepare source directories for images and labels
    image_source_dirs = []
    label_source_dirs = []

    for class_folder in CLASS_FOLDERS:
        class_path = DATASET_ROOT / class_folder / "train"
        if class_path.exists():
            image_source_dirs.append(class_path / "images")
            label_source_dirs.append(class_path / "labels")
        else:
            print(f"Warning: Class folder does not exist: {class_path}")

    if not image_source_dirs:
        print("Error: No valid class folders found to merge from.")
        sys.exit(1)

    # Merge images
    images_target = DATASET_ROOT / "merged" / "images"
    print(f"\nMerging images from {len(image_source_dirs)} class folders...")
    images_copied = merge_files(image_source_dirs, images_target, "images")
    print(f"Images: {images_copied} copied")
    print(f"Target: {images_target}")

    # Merge labels
    labels_target = DATASET_ROOT / "merged" / "labels"
    print(f"\nMerging labels from {len(label_source_dirs)} class folders...")
    labels_copied = merge_files(label_source_dirs, labels_target, "labels")
    print(f"Labels: {labels_copied} copied")
    print(f"Target: {labels_target}")

    print(f"\nDone. Merged {images_copied} images and {labels_copied} labels.")


if __name__ == "__main__":
    main()
