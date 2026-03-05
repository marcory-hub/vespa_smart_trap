**One-line purpose:** 
**Short summary:**
**Agent:** 
**SoT:**
**Main Index:**


---

# Pipeline: merge images and labels for Swift-YOLO (CVAT → COCO → Colab)

One-place reference for turning merged YOLO-style data (images + labels) into a Colab-ready COCO dataset.

**Location:** Scripts in `dataset_yolo_to_coco/`. Copy to your dataset folder (e.g. `dataset_vespa_2026-02v4_merge_yolo`) before running.

---

## 1. Starting layout

- **images:** `images/train/*.jpg` (or flat `images/*.jpg` in e.g. `datset_vespa_2026-02v4_merge_yolo`)
- **labels:** `labels/train/*.txt` (or flat `labels/*.txt`); YOLO format: one `.txt` per image, same base name. Do not rename files.
- **Classes:** 4 only: 0=amel, 1=vcra, 2=vespsp, 3=vvel. Null is background (no bbox, no class). `obj.names`: amel, vcra, vespsp, vvel.

---

## 2. Import into CVAT (YOLO 1.1)

CVAT expects a single folder per split with both images and annotation `.txt` files, plus a path list.

**2.1 Build CVAT-ready structure**

- Copy `dataset_yolo_to_coco/build_cvat_zip.sh` to your dataset folder and run it from there (e.g. `dataset_vespa_2026-02v4_merge_yolo`). It uses `images/train/` and `labels/train/` if present, otherwise `images/` and `labels/`. It:
  - Creates `obj_train_data/` with copies of each image and its matching `.txt` (no file renaming).
  - Writes `train.txt` with one line per image: `obj_train_data/<filename>.jpg`.
- Ensure `obj.data` and `obj.names` exist and have **no comment lines** (no `# ...` at the top). For 4 classes: amel, vcra, vespsp, vvel (null = background, not a class).

**2.2 Zip for upload**

From the dataset folder:

```bash
zip -r ../dataset_cvat_yolo.zip obj.data obj.names obj_train_data train.txt -x '*.DS_Store'
```

**2.3 In CVAT**

- Create a task with the same images (same filenames).
- Upload annotation → format **YOLO 1.1** → select the zip.

---

## 3. Export from CVAT as COCO

- In CVAT: Export dataset → format **COCO**.
- Free tier exports only the annotation JSON (no images). Save as `instances_train.json` in the dataset folder.

---

## 4. Convert to Colab-compatible COCO JSON

**4.1 Strip CVAT-only fields**

- CVAT adds `attributes` (e.g. `occluded`, `rotation`) to each annotation. The Colab pipeline expects standard COCO keys only.
- Copy `dataset_yolo_to_coco/convert_cvat_coco.py` to your dataset folder and run it. It:
  - Reads `dataset/instances_train.json` (or `instances_train.json` at root).
  - Removes `attributes` from every annotation.
  - Writes `_annotations.coco.json` (compact, no pretty-print).

**4.2 Class ids**

- CVAT export uses category ids **1–4** (amel=1, vcra=2, vespsp=3, vvel=4). The working Colab test file uses the same (1=amel, 2=vcra, 3=vespsp, 4=vvel). Use `_annotations.coco.json` as-is; do not use the 0–3 variant unless you need amel=0.

---

## 5. Direct YOLO to COCO conversion (when CVAT export unavailable)

**5.1 When to use this path**

- If CVAT upload fails (e.g., dataset too large for free tier) or you want to skip CVAT entirely.
- You have YOLO labels (`.txt` files) and images, but no `instances_train.json` from CVAT.

**5.2 Convert YOLO labels to COCO JSON and split**

- Copy `dataset_yolo_to_coco/yolo_to_coco_split.py` to your dataset folder and run it. It **never modifies the images folder** (read-only). It:
  - Reads images from `images/` and labels from `labels/` (both read-only).
  - Reads actual image dimensions (PIL) for accurate bbox conversion.
  - Converts YOLO format (class_id 0-3, normalized `cx cy w h`) to COCO format (category_id 1-4, absolute `[x, y, width, height]` pixels).
  - Shuffles with fixed seed (42), splits 85% train / 14% valid / 1% test.
  - Creates a new folder `dataset_vespa_2026-02v3_train_valid_test_coco/` (or similar) with:
    - `train/_annotations.coco.json`: COCO JSON for train split (images referenced by filename).
    - `valid/_annotations.coco.json`: COCO JSON for valid split.
    - `test/_annotations.coco.json`: COCO JSON for test split.
  - **No images are copied**; JSONs reference images by filename (images stay in original `images/` folder).

**5.3 Class ID mapping**

- YOLO: 0=amel, 1=vcra, 2=vespsp, 3=vvel
- COCO: 1=amel, 2=vcra, 3=vespsp, 4=vvel (matches CVAT export format)

---

## 6. Train / valid / test split (85% / 14% / 1%) — CVAT path

**6.1 Split images and annotations (when you have CVAT export)**

- Copy `dataset_yolo_to_coco/split_train_valid.py` to your dataset folder and run it. It **never modifies the images folder** (read-only). It:
  - Reads all image names from `images/` (flat layout) or `images/train/` if present.
  - Shuffles with fixed seed (42), splits 85% train / 14% valid / 1% test.
  - **Copies** (does not move) images into `images/train/`, `images/valid/`, and `images/test/`; original `images/` folder is left unchanged.
  - Builds per-split COCO JSONs:
    - `images/train/_annotations.coco.json`: only images and annotations in the train set.
    - `images/valid/_annotations.coco.json`: only images and annotations in the valid set.
    - `images/test/_annotations.coco.json`: only images and annotations in the test set.
- Each folder must list only the images it contains; duplicating the full JSON into both would make the loader try to open missing files and fail.

**6.2 Final layout after split (CVAT path)**

After running the split script, your dataset folder will have:

  ```
  images/
  ├── train/
  │   ├── _annotations.coco.json
  │   └── *.jpg
  ├── valid/
  │   ├── _annotations.coco.json
  │   └── *.jpg
  └── test/
      ├── _annotations.coco.json
      └── *.jpg
  ```

The original `images/` folder (with all 116540 images) remains unchanged; only subfolders are created with copies.

---

## 7. Zip for Colab (dataset.zip)

From the dataset folder (e.g. `dataset_vespa_2026-02v4_merge_yolo`):

```bash
zip -r dataset.zip images/train images/valid images/test -i '*.jpg' '*.json' -x '*.DS_Store' -x '*__MACOSX*' -x '._*'
```

- **Result:** `dataset.zip` containing only `.jpg` and `.json` from the split folders; no metadata (e.g. `.DS_Store`, `__MACOSX`, `._*`).
- Use this zip (or the unzipped `images/train`, `images/valid`, `images/test` on Drive) for Swift-YOLO Colab.

---

## Scripts and files (summary)

All scripts are in `dataset_yolo_to_coco/`. Copy them to your dataset folder before running.

| Item | Purpose |
|------|--------|
| `build_cvat_zip.sh` | Build `obj_train_data/` and `train.txt` from `images/` (or `images/train/`) + `labels/` for CVAT YOLO import. |
| `convert_cvat_coco.py` | Read `dataset/instances_train.json`, strip `attributes`, write `_annotations.coco.json` (and optional 0–3 class variant). |
| `split_train_valid.py` | 85%/14%/1% random split from `images/` into `images/train/`, `images/valid/`, `images/test/`, write per-split `_annotations.coco.json` (requires existing COCO JSON). |
| `yolo_to_coco_split.py` | Direct YOLO→COCO conversion + 85%/14%/1% split. Reads images/labels, converts bboxes, creates `train/valid/test/` folders with COCO JSONs (no image copies). |
| `obj.data`, `obj.names` | CVAT YOLO config; keep without leading `#` comment lines. |

---

## See also

- **CVAT YOLO format:** [docs.cvat.ai — format-yolo](https://docs.cvat.ai/docs/dataset_management/formats/format-yolo/)
- **Detailed notes and COCO comparison:** `notes/dataset cvat yolo format.md`
