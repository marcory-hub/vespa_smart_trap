#!/usr/bin/env python3
"""
Merge images and labels from class-specific folders into consolidated folders.

Merges images from original.vXi.yolo26/{class}.vXi.yolo26/images/ into
original.vXi.yolo26/images.vXi.yolo26/, and labels from
original.vXi.yolo26/{class}.vXi.yolo26/labels/ into
original.vXi.yolo26/labels.vXi.yolo26/.

Handles filename conflicts by skipping duplicates and logging warnings.
Auto-detects v3 vs v4 from dataset root path.
- v3: uses v3i.yolo26, 4 classes (amel, vcra, vespsp, vvel)
- v4: uses v4i.yolo26, 5 classes (amel, vcra, vespsp, vvel, null)
"""
import argparse
import shutil
import sys
from pathlib import Path

# Class folders for v3 (4 classes, no null)
CLASS_FOLDERS_V3 = [
    "amel.v3i.yolo26",
    "vcra.v3i.yolo26",
    "vespsp.v3i.yolo26",
    "vvel.v3i.yolo26",
]

# Class folders for v4 (5 classes, includes null)
CLASS_FOLDERS_V4 = [
    "amel.v4i.yolo26",
    "vcra.v4i.yolo26",
    "vespsp.v4i.yolo26",
    "vvel.v4i.yolo26",
    "null.v4i.yolo26",
]


def merge_files(
    source_dirs: list[Path],
    target_dir: Path,
    file_type: str,
) -> tuple[int, int]:
    """
    Merge files from multiple source directories into a target directory.

    Args:
        source_dirs: List of source directories to merge from
        target_dir: Target directory to merge into
        file_type: Description of file type for logging ("images" or "labels")

    Returns:
        Tuple of (files_copied, conflicts_skipped)
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    seen_filenames = set()
    files_copied = 0
    conflicts_skipped = 0

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
            print(f"  {source_dir.name}: No {file_type} found")
            continue

        print(f"  Processing {source_dir.name}: {total_files} {file_type}...", end="", flush=True)

        for idx, source_file in enumerate(files, 1):
            filename = source_file.name
            target_file = target_dir / filename

            if filename in seen_filenames:
                conflicts_skipped += 1
                if conflicts_skipped <= 5:  # Only print first 5 conflicts to avoid spam
                    print(f"\n    Warning: Skipping duplicate {file_type} file: {filename}")
                continue

            # Copy file and track it
            shutil.copy2(source_file, target_file)
            seen_filenames.add(filename)
            files_copied += 1

            # Progress indicator every 100 files
            if idx % 100 == 0 or idx == total_files:
                print(f" {idx}/{total_files}", end="", flush=True)

        print(f" ✓ ({files_copied} total copied so far)")

    return files_copied, conflicts_skipped


def detect_version(dataset_root: Path) -> tuple[str, list[str]]:
    """
    Detect dataset version (v3 or v4) from dataset root path and return version suffix and class folders.

    Args:
        dataset_root: Path to dataset root directory

    Returns:
        Tuple of (version_suffix, class_folders_list)
        version_suffix is "v3i.yolo26" or "v4i.yolo26"
    """
    dataset_name = dataset_root.name

    # Check for v3 in path (e.g., dataset_vespa_2026-02v3_train_val_test_yolo)
    if "v3" in dataset_name and "v4" not in dataset_name:
        return "v3i.yolo26", CLASS_FOLDERS_V3
    # Check for v4 in path (e.g., dataset_vespa_2026-02v4_train_val_test_yolo)
    elif "v4" in dataset_name:
        return "v4i.yolo26", CLASS_FOLDERS_V4
    else:
        # Try to detect by checking which original directory exists
        v3_dir = dataset_root / "original.v3i.yolo26"
        v4_dir = dataset_root / "original.v4i.yolo26"
        if v3_dir.exists() and not v4_dir.exists():
            return "v3i.yolo26", CLASS_FOLDERS_V3
        elif v4_dir.exists() and not v3_dir.exists():
            return "v4i.yolo26", CLASS_FOLDERS_V4
        else:
            # Default to v4 if ambiguous
            print("Warning: Could not detect version from path, defaulting to v4")
            return "v4i.yolo26", CLASS_FOLDERS_V4


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge images and labels from class-specific folders into consolidated folders."
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

    # Detect version and get appropriate class folders
    version_suffix, class_folders = detect_version(dataset_root)
    original_dir = dataset_root / f"original.{version_suffix}"

    if not original_dir.exists():
        print(f"Error: Original directory does not exist: {original_dir}")
        print(f"Detected version suffix: {version_suffix}")
        sys.exit(1)

    print(f"Detected version: {version_suffix} ({len(class_folders)} classes)")

    # Prepare source directories for images and labels
    image_source_dirs = []
    label_source_dirs = []

    for class_folder in class_folders:
        class_path = original_dir / class_folder
        if class_path.exists():
            image_source_dirs.append(class_path / "images")
            label_source_dirs.append(class_path / "labels")
        else:
            print(f"Warning: Class folder does not exist: {class_path}")

    if not image_source_dirs:
        print("Error: No valid class folders found to merge from.")
        sys.exit(1)

    # Merge images
    images_target = original_dir / f"images.{version_suffix}"
    print(f"\nMerging images from {len(image_source_dirs)} class folders...")
    images_copied, images_conflicts = merge_files(image_source_dirs, images_target, "images")
    print(f"Images: {images_copied} copied, {images_conflicts} conflicts skipped")
    print(f"Target: {images_target}")

    # Merge labels
    labels_target = original_dir / f"labels.{version_suffix}"
    print(f"\nMerging labels from {len(label_source_dirs)} class folders...")
    labels_copied, labels_conflicts = merge_files(label_source_dirs, labels_target, "labels")
    print(f"Labels: {labels_copied} copied, {labels_conflicts} conflicts skipped")
    print(f"Target: {labels_target}")

    print(f"\nDone. Merged {images_copied} images and {labels_copied} labels.")


if __name__ == "__main__":
    main()
