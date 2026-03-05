#!/usr/bin/env python3
"""Split images 85% train / 15% valid and write per-split COCO JSONs.
Source: images/train/*.jpg and _annotations.coco.json.
Output: train/, valid/ with images and _annotations.coco.json each.
Colab expects each folder to list only the images it contains (missing files would error).
"""
import json
import os
import random
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT, "images", "train")
TRAIN_DIR = os.path.join(ROOT, "train")
VALID_DIR = os.path.join(ROOT, "valid")
ANN_PATH = os.path.join(ROOT, "_annotations.coco.json")
RANDOM_SEED = 42
TRAIN_FRAC = 0.85

def main():
    random.seed(RANDOM_SEED)
    with open(ANN_PATH) as f:
        data = json.load(f)

    # All image file names present on disk
    all_names = [f for f in os.listdir(SRC_DIR) if f.lower().endswith(".jpg")]
    if not all_names:
        raise SystemExit(f"No .jpg in {SRC_DIR}")
    random.shuffle(all_names)
    n = len(all_names)
    n_train = int(round(n * TRAIN_FRAC))
    train_names = set(all_names[:n_train])
    valid_names = set(all_names[n_train:])

    os.makedirs(TRAIN_DIR, exist_ok=True)
    os.makedirs(VALID_DIR, exist_ok=True)

    for name in train_names:
        shutil.copy2(os.path.join(SRC_DIR, name), os.path.join(TRAIN_DIR, name))
    for name in valid_names:
        shutil.copy2(os.path.join(SRC_DIR, name), os.path.join(VALID_DIR, name))

    # Build split JSONs: only images and annotations for that split
    img_by_name = {im["file_name"]: im for im in data["images"]}
    img_id_to_img = {im["id"]: im for im in data["images"]}
    anns_by_img_id = {}
    for ann in data["annotations"]:
        anns_by_img_id.setdefault(ann["image_id"], []).append(ann)

    for split_name, names in [("train", train_names), ("valid", valid_names)]:
        out_dir = TRAIN_DIR if split_name == "train" else VALID_DIR
        images = [img_by_name[n] for n in names if n in img_by_name]
        img_ids = {im["id"] for im in images}
        annotations = []
        for iid in img_ids:
            annotations.extend(anns_by_img_id.get(iid, []))
        out_data = {
            "licenses": data["licenses"],
            "info": data["info"],
            "categories": data["categories"],
            "images": images,
            "annotations": annotations,
        }
        out_path = os.path.join(out_dir, "_annotations.coco.json")
        with open(out_path, "w") as f:
            json.dump(out_data, f, separators=(",", ":"))
        print(f"{split_name}: {len(images)} images, {len(annotations)} annotations -> {out_path}")

    print(f"Done. train={len(train_names)} valid={len(valid_names)} (seed={RANDOM_SEED})")

if __name__ == "__main__":
    main()
