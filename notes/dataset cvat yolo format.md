
**One-line purpose:** make dataset format and zip it for import in cvat
**Key info:** 
**Agent:** here you find information about how to make the cvat yolo dataset

---

1. first tackle problem how to format the dataset
https://docs.cvat.ai/docs/dataset_management/formats/format-yolo/
https://app.cvat.ai/requests?page=1&pageSize=10
**cvat.apps.dataset_manager.bindings.CvatDatasetNotFoundError: Check [format docs]**

You find the instructions how to format that folder structure, the data files here: https://docs.cvat.ai/docs/dataset_management/formats/format-yolo/

Download a .zip archive with the following structure
```
archive.zip/
├── obj.data
├── obj.names
├── obj_<subset>_data
│   ├── image1.txt
│   └── image2.txt
└── train.txt # list of subset image paths

# the only valid subsets are: train, valid
# train.txt and valid.txt:
obj_<subset>_data/image1.jpg
obj_<subset>_data/image2.jpg

# obj.data:
classes = 3 # optional
names = obj.names
train = train.txt
valid = valid.txt # optional
backup = backup/ # optional

# obj.names:
cat
dog
airplane

# image_name.txt:
# label_id - id from obj.names
# cx, cy - relative coordinates of the bbox center
# rw, rh - relative size of the bbox
# label_id cx cy rw rh
1 0.3 0.8 0.1 0.3
2 0.7 0.2 0.3 0.1

```

**Folder of the dataset** /Users/md/Developer/vespa_smart_trap/dataset_vespa_2026-02_cvat_merged_yolo

**Current folder structure**
```
dataset/
├── images/
│   └── train/
│       ├── amel1_0000_jpg.rf.70bb4600c8483067ff89b7ede04ed8ca.jpg
│       ├── amel1_0001_jpg.rf.1fdd637bf6bf94c084366f0738ea4598.jpg
│       └── ...
├── labels/
│   └── train/
│       ├── amel1_0000_jpg.rf.70bb4600c8483067ff89b7ede04ed8ca.txt
│       ├── amel1_0001_jpg.rf.1fdd637bf6bf94c084366f0738ea4598.txt
│       └── ...
├── obj.data
└── obj.names
```

**Current obj.names** 
```
# obj.names:
amel
vcra
vespsp
vvel
```

**Current obj.data** (no leading `#` lines; CVAT parser may fail on comments)
```
classes = 4
names = obj.names
train = train.txt
```

---

## CVAT import: required zip structure (fix for CvatDatasetNotFoundError)

CVAT expects the **exact** layout below. Using `images/` and `labels/` subfolders causes "Check [format docs]".

**Required layout inside the zip:**
```
archive.zip/
├── obj.data
├── obj.names
├── obj_train_data/          # one folder per subset (name = obj_<subset>_data)
│   ├── image1.jpg
│   ├── image1.txt
│   ├── image2.jpg
│   └── image2.txt
└── train.txt                # paths like obj_train_data/image1.jpg (one per line)
```

- **obj.data** / **obj.names**: no comment lines at the top (strip `# ...`).
- **train.txt**: must exist and list image paths as `obj_train_data/<filename>.jpg`.
- **obj_train_data**: must contain both `.jpg` and `.txt` (same base name per image).

**Build steps (from dataset folder):**
1. Run `./build_cvat_zip.sh` to create `obj_train_data` (copy of images + labels) and `train.txt`.
2. Zip only the CVAT files (do not zip `images/`, `labels/`, or `.yaml`):
   ```bash
   zip -r ../dataset_cvat_yolo.zip obj.data obj.names obj_train_data train.txt -x '*.DS_Store'
   ```
3. In CVAT: Upload annotation → format **YOLO 1.1** → select the zip. Task must already exist and contain the same images (same filenames) so frame names match.

**Previous failing zip command** (wrong contents for CVAT):
- `zip -r ../dataset.zip . -i '*.jpg' '*.txt' '*.yaml' '*/'` — includes wrong layout (images/labels) and no train.txt; CVAT expects obj_train_data + train.txt.

---

## COCO: instances_train.json (CVAT export) vs _annotations_*.coco.json (Colab-working)

Compared: `dataset_vespa_2026-02_cvat_merged_yolo/instances_train.json` (CVAT COCO export) vs `_annotations_null.coco.json` and `_annotations_amel.coco.json` (Roboflow-style; work in Swift-YOLO Colab).

**Top-level:** Same keys: info, licenses, categories, images, annotations. Key order differs (CVAT: licenses first; Roboflow: info first). Unlikely to affect loading.

**categories**
| | instances_train (CVAT) | _annotations_*.coco (Roboflow) |
|--|------------------------|--------------------------------|
| ids | 1–4 only (amel, vcra, vespsp, vvel) | null: single id 0 "objects". amel: id 0 "objects" + 1–4 (amel, vcra, vespsp, vvel) |
| supercategory | "" | "none" or "objects" |

**images**
| | instances_train (CVAT) | _annotations_*.coco (Roboflow) |
|--|------------------------|--------------------------------|
| id | 1-based (1, 2, …) | 0-based (0, 1, …) |
| keys | id, width, height, file_name, license, flickr_url, coco_url, date_captured | id, license, file_name, height, width, date_captured, **extra** |
| license | 0 | 1 |
| date_captured | 0 (number) | ISO string e.g. "2026-01-30T19:52:49+00:00" |
| extra | absent | present: `{"name":"original_filename.jpg"}` |

**annotations**
| | instances_train (CVAT) | _annotations_amel (Roboflow) |
|--|------------------------|------------------------------|
| keys | id, image_id, category_id, segmentation, area, bbox, iscrowd, **attributes** | id, image_id, category_id, bbox, area, segmentation, iscrowd |
| attributes | `{"occluded": false, "rotation": 0.0}` | absent |
| bbox | [x, y, w, h] (COCO) | [x, y, w, h] (COCO) |

**Summary of differences that may matter for Colab**
1. **annotations.attributes** — CVAT adds this; Roboflow does not. If the Colab loader expects only standard COCO keys, strip `attributes` from each annotation.
2. **images: extra** — Roboflow has `extra.name`; CVAT does not. Only needed if your pipeline uses it.
3. **images: id** — CVAT 1-based, Roboflow 0-based. Colab/mmdet usually use image_id as reference; as long as annotation `image_id` matches the corresponding image `id`, both are valid.
4. **categories** — Roboflow amel has id 0 "objects" plus 1–4; CVAT has only 1–4. If the config expects a background class 0, you may need to add a "objects" (or ignore) category with id 0; otherwise 1–4 is standard for four classes.

**Minimal conversion (if Colab fails on instances_train.json):** Remove `attributes` from every annotation; optionally normalize image ids to 0-based and add `extra` / adjust categories to match the working JSONs. Do not pretty-print the JSON (keep one line or compact) for Swift-YOLO.

---

## Train / valid split (Swift-YOLO Colab)

- **Script:** `dataset_vespa_2026-02_cvat_merged_yolo/split_train_valid.py` — random 85% train, 15% valid (seed=42). Copies from `images/train/` into `train/` and `valid/`, and writes `train/_annotations.coco.json` and `valid/_annotations.coco.json`.
- **JSON per folder:** We must split the annotation file: each folder’s `_annotations.coco.json` lists only the images (and their annotations) in that folder. Duplicating the full JSON into both folders would reference missing images in each (train would list the 15% that moved to valid, and vice versa); the Colab loader would then try to open missing files and fail. So each split has its own filtered JSON.

