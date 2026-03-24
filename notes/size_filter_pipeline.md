**One-line purpose:** 
**Short summary:**
**SoT:**
**Agent:** 
**Main Index:**

---

# Size-filtered datasets (30px / 40px / 60px)

**One-line purpose:** Pipeline and naming for YOLO datasets filtered by minimum object size (for 192x192 training). [[_datasets_vst]]

**Percentages (relative to 192 px):**
- 30 px -> 15.6% -> **16%** -> merged_30px -> dataset_vespa_2026-02v1_30px_nopre_aug_train_valid_test_yolo
- 40 px -> 20.8% -> **21%** -> merged_40px -> dataset_vespa_2026-02v1_40px_nopre_aug_train_valid_test_yolo
- 60 px -> 31.25% -> **31%** -> merged_60px -> dataset_vespa_2026-02v1_60px_nopre_aug_train_valid_test_yolo

**Pipeline (run in order):** All scripts preserve .jpg and .txt filenames (no renaming). Output dirs are not overwritten unless `--overwrite` is given.
1. **Merge:** `merge_vespa_to_merged.py` — Copies from `dataset_vespa/{train,valid,test}/images` and `.../labels` into a single flat `dataset_vespa/merged/images` and `dataset_vespa/merged/labels` (no train/valid/test subdirs). All image names are unique. Source read-only.
2. **Filter:** `filter_by_bbox_size.py` — Reads flat merged/images and merged/labels, keeps images where at least one bbox has `size_frac >= threshold`. Writes flat `merged_30px/images`, `merged_30px/labels` (and 40px, 60px). Images without labels excluded.
3. **Split:** `split_size_filtered_to_train_valid_test.py` — From each flat `merged_*`, splits 85% train / 14% valid / 1% test (seed=42) into final datasets at workspace root with `train/images`, `train/labels`, `valid/...`, `test/...`.

**CLI (from repo root):**
```bash
source .venv/bin/activate
cd scripts/split_yolo_train_val_test
python3 merge_vespa_to_merged.py
python3 filter_by_bbox_size.py
python3 split_size_filtered_to_train_valid_test.py
```
Re-run with `--overwrite` to replace existing merged/ or merged_* or target dataset content.
