#!/usr/bin/env python3
"""
Filter merged images by minimum object size (as fraction of image max dimension).

Reads dataset_vespa/merged/images and merged/labels (flat, no train/valid/test).
For each image, loads dimensions and YOLO labels; computes per bbox
size_frac = max(bbox_w, bbox_h) / max(img_w, img_h). Keeps image if at least one bbox
has size_frac >= threshold. Images without labels are excluded. Writes to flat
dataset_vespa/merged_30px/images, merged_30px/labels (and 40px, 60px).
Filenames preserved. Exits if output folders already have content unless --overwrite.
"""
import argparse
import shutil
from pathlib import Path

from PIL import Image

WORKSPACE = Path(__file__).resolve().parents[2]
# All merge/filter outputs live inside dataset_vespa (flat images/ and labels/)
SOURCE_ROOT = WORKSPACE / "dataset_vespa"
MERGED_IMAGES = SOURCE_ROOT / "merged" / "images"
MERGED_LABELS = SOURCE_ROOT / "merged" / "labels"
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")

# threshold (min size as fraction of max image dimension) -> output folder name under dataset_vespa
THRESHOLDS = [
    (0.16, "merged_30px"),   # dataset_vespa/merged_30px
    (0.21, "merged_40px"),   # dataset_vespa/merged_40px
    (0.31, "merged_60px"),   # dataset_vespa/merged_60px
]


def parse_yolo_label(label_path: Path) -> list[tuple[float, float, float, float]]:
    """Return list of (w_norm, h_norm) per line (class_id x_center y_center w h)."""
    if not label_path.exists():
        return []
    rows = []
    for line in label_path.read_text().strip().splitlines():
        parts = line.split()
        if len(parts) >= 5:
            try:
                w_norm = float(parts[3])
                h_norm = float(parts[4])
                rows.append((w_norm, h_norm))
            except ValueError:
                continue
    return rows


def max_bbox_size_frac(img_path: Path, label_path: Path) -> float | None:
    """
    Return max over all bboxes of size_frac, or None if no labels or image missing.
    size_frac = max(bbox_w, bbox_h) / max(img_w, img_h); bbox in pixels from normalized.
    """
    if not img_path.exists():
        return None
    try:
        with Image.open(img_path) as im:
            img_w, img_h = im.size
    except Exception:
        return None
    max_dim = max(img_w, img_h)
    if max_dim <= 0:
        return None
    rows = parse_yolo_label(label_path)
    if not rows:
        return None
    best = 0.0
    for w_norm, h_norm in rows:
        bbox_w = w_norm * img_w
        bbox_h = h_norm * img_h
        size_frac = max(bbox_w, bbox_h) / max_dim
        if size_frac > best:
            best = size_frac
    return best


def collect_merged_pairs() -> list[tuple[Path, Path]]:
    """Collect (image_path, label_path) from flat merged/images and merged/labels."""
    pairs = []
    if not MERGED_IMAGES.is_dir():
        return pairs
    for ext in IMAGE_EXTENSIONS:
        for img_path in MERGED_IMAGES.glob(f"*{ext}"):
            if not img_path.is_file():
                continue
            label_path = MERGED_LABELS / (img_path.stem + ".txt")
            if label_path.exists():
                pairs.append((img_path, label_path))
    return pairs


def filtered_has_content() -> bool:
    """True if any merged_* folder already has files (flat images/)."""
    for _thresh, folder_name in THRESHOLDS:
        images_dir = SOURCE_ROOT / folder_name / "images"
        if images_dir.is_dir() and any(images_dir.iterdir()):
            return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Filter merged by min bbox size; preserve filenames.")
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting existing merged_* content.")
    args = parser.parse_args()

    if not MERGED_IMAGES.is_dir():
        print(f"Error: Merged images not found: {MERGED_IMAGES}")
        return
    if not MERGED_LABELS.is_dir():
        print(f"Error: Merged labels not found: {MERGED_LABELS}")
        return

    pairs = collect_merged_pairs()
    if not pairs:
        print("No image+label pairs in merged.")
        return

    if filtered_has_content() and not args.overwrite:
        print("Output merged_30px/merged_40px/merged_60px already have content. Run with --overwrite to replace.")
        return

    for threshold, folder_name in THRESHOLDS:
        out_images = SOURCE_ROOT / folder_name / "images"
        out_labels = SOURCE_ROOT / folder_name / "labels"
        out_images.mkdir(parents=True, exist_ok=True)
        out_labels.mkdir(parents=True, exist_ok=True)
        kept = 0
        for img_path, lbl_path in pairs:
            frac = max_bbox_size_frac(img_path, lbl_path)
            if frac is not None and frac >= threshold:
                shutil.copy2(img_path, out_images / img_path.name)
                shutil.copy2(lbl_path, out_labels / lbl_path.name)
                kept += 1
        print(f"{folder_name} (threshold {threshold:.2%}): {kept} / {len(pairs)} kept")


if __name__ == "__main__":
    main()
