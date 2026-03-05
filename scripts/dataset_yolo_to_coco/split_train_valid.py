#!/usr/bin/env python3
"""Split images 85% train / 14% valid / 1% test and write per-split COCO JSONs.
Source: images/*.jpg (flat) and _annotations.coco.json (read-only; never modify images).
Output: images/train/, images/valid/, images/test/ with copies and _annotations.coco.json each.
Colab expects each folder to list only the images it contains (missing files would error).
"""
import json
import os
import random
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT, "images")
TRAIN_DIR = os.path.join(ROOT, "images", "train")
VALID_DIR = os.path.join(ROOT, "images", "valid")
TEST_DIR = os.path.join(ROOT, "images", "test")
ANN_PATH = os.path.join(ROOT, "_annotations.coco.json")
RANDOM_SEED = 42
TRAIN_FRAC = 0.85
VALID_FRAC = 0.14

def main():
    # Never write or delete inside images; it is the immutable source of truth.
    for d in (TRAIN_DIR, VALID_DIR, TEST_DIR):
        if os.path.commonpath([os.path.realpath(SRC_DIR), os.path.realpath(d)]) == os.path.realpath(SRC_DIR):
            if os.path.realpath(d) == os.path.realpath(SRC_DIR):
                raise SystemExit("Refusing to run: output dir would overwrite images. Images must not be modified.")
    random.seed(RANDOM_SEED)
    with open(ANN_PATH) as f:
        data = json.load(f)

    # All image file names present on disk (read-only listdir)
    all_names = [f for f in os.listdir(SRC_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    if not all_names:
        raise SystemExit(f"No .jpg/.jpeg/.png in {SRC_DIR}")
    random.shuffle(all_names)
    n = len(all_names)
    n_train = int(round(n * TRAIN_FRAC))
    n_valid = int(round(n * VALID_FRAC))
    train_names = set(all_names[:n_train])
    valid_names = set(all_names[n_train:n_train + n_valid])
    test_names = set(all_names[n_train + n_valid:])

    os.makedirs(TRAIN_DIR, exist_ok=True)
    os.makedirs(VALID_DIR, exist_ok=True)
    os.makedirs(TEST_DIR, exist_ok=True)

    for name in train_names:
        shutil.copy2(os.path.join(SRC_DIR, name), os.path.join(TRAIN_DIR, name))
    for name in valid_names:
        shutil.copy2(os.path.join(SRC_DIR, name), os.path.join(VALID_DIR, name))
    for name in test_names:
        shutil.copy2(os.path.join(SRC_DIR, name), os.path.join(TEST_DIR, name))

    # Build split JSONs: only images and annotations for that split
    img_by_name = {im["file_name"]: im for im in data["images"]}
    anns_by_img_id = {}
    for ann in data["annotations"]:
        anns_by_img_id.setdefault(ann["image_id"], []).append(ann)

    for split_name, names in [("train", train_names), ("valid", valid_names), ("test", test_names)]:
        if split_name == "train":
            out_dir = TRAIN_DIR
        elif split_name == "valid":
            out_dir = VALID_DIR
        else:
            out_dir = TEST_DIR
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

    print(f"Done. train={len(train_names)} valid={len(valid_names)} test={len(test_names)} (seed={RANDOM_SEED})")

if __name__ == "__main__":
    main()
