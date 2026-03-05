#!/usr/bin/env python3
"""Convert YOLO labels to COCO JSON format and split 85%/14%/1%.
Reads from images/ and labels/ (read-only), writes train/valid/test/ with images and _annotations.coco.json.
YOLO: class_id 0-3 (amel, vcra, vespsp, vvel), normalized cx cy w h.
COCO: category_id 1-4 (amel=1, vcra=2, vespsp=3, vvel=4), absolute x y w h in pixels.
"""
import json
import os
import random
import shutil
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_IMG_DIR = os.path.join(ROOT, "images")
SRC_LBL_DIR = os.path.join(ROOT, "labels")
OUT_ROOT = os.path.join(os.path.dirname(ROOT), "dataset_vespa_2026-02v3_train_valid_test_coco")
RANDOM_SEED = 42
TRAIN_FRAC = 0.85
VALID_FRAC = 0.14

# YOLO class_id -> COCO category_id mapping
YOLO_TO_COCO = {0: 1, 1: 2, 2: 3, 3: 4}  # amel=1, vcra=2, vespsp=3, vvel=4

def yolo_to_coco_bbox(cx_norm, cy_norm, w_norm, h_norm, img_width, img_height):
    """Convert YOLO normalized bbox to COCO absolute bbox [x, y, width, height]."""
    # YOLO: center (cx, cy) and size (w, h), all normalized 0-1
    # COCO: top-left (x, y) and size (width, height), absolute pixels
    w_px = w_norm * img_width
    h_px = h_norm * img_height
    x_px = (cx_norm * img_width) - (w_px / 2)
    y_px = (cy_norm * img_height) - (h_px / 2)
    # Ensure bbox is within image bounds
    x_px = max(0, min(x_px, img_width - 1))
    y_px = max(0, min(y_px, img_height - 1))
    w_px = max(1, min(w_px, img_width - x_px))
    h_px = max(1, min(h_px, img_height - y_px))
    return [x_px, y_px, w_px, h_px]

def main():
    random.seed(RANDOM_SEED)
    os.makedirs(OUT_ROOT, exist_ok=True)
    
    # Get all image files
    all_images = [f for f in os.listdir(SRC_IMG_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not all_images:
        raise SystemExit(f"No images in {SRC_IMG_DIR}")
    random.shuffle(all_images)
    n = len(all_images)
    n_train = int(round(n * TRAIN_FRAC))
    n_valid = int(round(n * VALID_FRAC))
    train_images = all_images[:n_train]
    valid_images = all_images[n_train:n_train + n_valid]
    test_images = all_images[n_train + n_valid:]
    
    categories = [
        {"id": 1, "name": "amel", "supercategory": ""},
        {"id": 2, "name": "vcra", "supercategory": ""},
        {"id": 3, "name": "vespsp", "supercategory": ""},
        {"id": 4, "name": "vvel", "supercategory": ""},
    ]
    
    for split_name, image_list in [("train", train_images), ("valid", valid_images), ("test", test_images)]:
        out_dir = os.path.join(OUT_ROOT, split_name)
        os.makedirs(out_dir, exist_ok=True)
        
        images = []
        annotations = []
        img_id_counter = 1
        ann_id_counter = 1
        
        for img_name in image_list:
            img_path = os.path.join(SRC_IMG_DIR, img_name)
            base_name = os.path.splitext(img_name)[0]
            lbl_path = os.path.join(SRC_LBL_DIR, base_name + ".txt")
            
            # Read image dimensions and copy image
            try:
                with Image.open(img_path) as img:
                    width, height = img.size
            except Exception as e:
                print(f"Warning: Could not read {img_name}: {e}")
                continue
            
            # Copy image to split folder (images folder remains read-only)
            shutil.copy2(img_path, os.path.join(out_dir, img_name))
            
            # Add image entry
            images.append({
                "id": img_id_counter,
                "width": width,
                "height": height,
                "file_name": img_name,
                "license": 0,
                "flickr_url": "",
                "coco_url": "",
                "date_captured": 0,
            })
            
            # Read and convert YOLO labels
            if os.path.isfile(lbl_path):
                with open(lbl_path) as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        parts = line.split()
                        if len(parts) < 5:
                            continue
                        try:
                            yolo_class_id = int(parts[0])
                            cx_norm, cy_norm, w_norm, h_norm = map(float, parts[1:5])
                            
                            # Convert to COCO
                            if yolo_class_id not in YOLO_TO_COCO:
                                continue
                            coco_category_id = YOLO_TO_COCO[yolo_class_id]
                            bbox = yolo_to_coco_bbox(cx_norm, cy_norm, w_norm, h_norm, width, height)
                            area = bbox[2] * bbox[3]  # width * height
                            
                            annotations.append({
                                "id": ann_id_counter,
                                "image_id": img_id_counter,
                                "category_id": coco_category_id,
                                "segmentation": [],
                                "area": area,
                                "bbox": bbox,
                                "iscrowd": 0,
                            })
                            ann_id_counter += 1
                        except (ValueError, IndexError) as e:
                            print(f"Warning: Invalid label line in {lbl_path}: {line}")
                            continue
            
            img_id_counter += 1
        
        # Build COCO JSON
        coco_data = {
            "licenses": [{"name": "", "id": 0, "url": ""}],
            "info": {
                "contributor": "",
                "date_created": "",
                "description": "",
                "url": "",
                "version": "",
                "year": "",
            },
            "categories": categories,
            "images": images,
            "annotations": annotations,
        }
        
        out_path = os.path.join(out_dir, "_annotations.coco.json")
        with open(out_path, "w") as f:
            json.dump(coco_data, f, separators=(",", ":"))
        
        print(f"{split_name}: {len(images)} images, {len(annotations)} annotations -> {out_path}")
    
    print(f"\nDone. train={len(train_images)} valid={len(valid_images)} test={len(test_images)} (seed={RANDOM_SEED})")
    print(f"Output: {OUT_ROOT}")

if __name__ == "__main__":
    main()
