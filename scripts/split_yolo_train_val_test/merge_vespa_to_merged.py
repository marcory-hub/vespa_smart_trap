#!/usr/bin/env python3
"""
Merge images and labels from dataset_vespa train/valid/test into a single flat pool.

Reads dataset_vespa/{train,valid,test}/images and .../labels (read-only).
Copies all into dataset_vespa/merged/images and dataset_vespa/merged/labels (no
train/valid/test subdirs). All images are assumed to have unique names.
Only copies image+label pairs that have both image and matching .txt.
If merged/ already contains files, exits unless --overwrite is given.
"""
import argparse
import shutil
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
# Merged output: single flat dataset_vespa/merged/images and merged/labels
SOURCE_ROOT = WORKSPACE / "dataset_vespa"
MERGED_IMAGES = SOURCE_ROOT / "merged" / "images"
MERGED_LABELS = SOURCE_ROOT / "merged" / "labels"
SPLITS = ("train", "valid", "test")
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


def collect_pairs(split_name: str) -> list[tuple[Path, Path]]:
    """Collect (image_path, label_path) for split; only pairs with both image and .txt."""
    images_dir = SOURCE_ROOT / split_name / "images"
    labels_dir = SOURCE_ROOT / split_name / "labels"
    if not images_dir.is_dir():
        return []
    pairs = []
    for ext in IMAGE_EXTENSIONS:
        for img_path in images_dir.glob(f"*{ext}"):
            if not img_path.is_file():
                continue
            label_path = labels_dir / (img_path.stem + ".txt")
            if label_path.exists():
                pairs.append((img_path, label_path))
    return pairs


def merged_has_content() -> bool:
    """True if merged/images or merged/labels has any files."""
    return MERGED_IMAGES.is_dir() and any(MERGED_IMAGES.iterdir())


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge dataset_vespa splits into flat merged/ (preserves filenames).")
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting existing merged/ content.")
    args = parser.parse_args()

    if not SOURCE_ROOT.is_dir():
        print(f"Error: Source not found: {SOURCE_ROOT}")
        return

    if merged_has_content() and not args.overwrite:
        print("Output merged/ already has content. Run with --overwrite to replace.")
        return

    MERGED_IMAGES.mkdir(parents=True, exist_ok=True)
    MERGED_LABELS.mkdir(parents=True, exist_ok=True)
    total_copied = 0
    for split_name in SPLITS:
        pairs = collect_pairs(split_name)
        for img_path, lbl_path in pairs:
            shutil.copy2(img_path, MERGED_IMAGES / img_path.name)
            shutil.copy2(lbl_path, MERGED_LABELS / lbl_path.name)
            total_copied += 1
        print(f"{split_name}: {len(pairs)} pairs copied (filenames preserved)")

    print(f"Total: {total_copied} image+label pairs in {MERGED_IMAGES} and {MERGED_LABELS}")


if __name__ == "__main__":
    main()
