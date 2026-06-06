# Review dataset_top folder placement

Manually verify that images in `data/dataset_top` are in the correct **top** vs **other** physical folders (six folders across train/val/test). NULL folders are not reviewed.

## Run

From the repo root:

```bash
source .venv/bin/activate
pip install opencv-python   # if not already installed
python scripts/dataset_top_select/review_folder_placement.py \
  --dataset-root data/dataset_top
```

## Keys

| Key | Action |
|-----|--------|
| **T** | Image is top-down view → move to `{split}_top` if currently in other folder |
| **O** | Image is other (side) view → move to `train_oth` / `val_other` / `test_oth` if currently in top folder |
| **N** or **Space** | Placement is correct → mark reviewed, no move |
| **B** | Step back to previous image for re-review (removes it from reviewed set) |
| **Q** | Save state and quit |

If **T** is pressed while already in a `*_top` folder (or **O** while already in `*_oth` / `val_other`), the image is marked reviewed and the tool advances (no move).


## Start at a specific image

Use a **1-based** index in the full sorted queue (same order every run: split, folder, filename):

```bash
python scripts/dataset_top_select/review_folder_placement.py \
  --dataset-root data/dataset_top \
  --start-at 5352
```

Images **1 .. 5351** are marked reviewed and saved to state before the UI opens. Combine with `--reset` for a clean slate except the skip, or without `--reset` to jump forward from existing progress.


## Archive reviewed images

Reviewed images live in `images_reviewed/` and `labels_reviewed/` (same subfolder names as `images/`).

- **During review:** **N**, **Space**, **T**, or **O** archives into `images_reviewed/` automatically.
- **Step back (B):** restores the previous image from `images_reviewed/` back into `images/`.
- **Bulk archive** (all logs + queue sequence):

```bash
python scripts/dataset_top_select/archive_reviewed_from_state.py \
  --dataset-root data/dataset_top --dry-run
python scripts/dataset_top_select/archive_reviewed_from_state.py \
  --dataset-root data/dataset_top
```

Uses: `reviewed[]` and `moves[]` in `.review_folder_placement.json`, all lines in `review_moves.log`, and (by default) every image from queue position **1** through the furthest position seen in those logs (covers **marked correct** with no move line). Use `--no-sequence` to skip sequence fill.

Log: `data/dataset_top/archive_reviewed.log`


## Restore unreviewed images (resume after bulk archive)

If images were archived into `images_reviewed/` without being marked in `reviewed[]`
(e.g. after `archive_reviewed_from_state.py` sequence fill), the reviewer restores
them automatically on startup (**default: on**).

Preview how many would move back:

```bash
python scripts/dataset_top_select/review_folder_placement.py \
  --dataset-root data/dataset_top \
  --restore-unreviewed-only --dry-run
```

Restore only (no UI):

```bash
python scripts/dataset_top_select/review_folder_placement.py \
  --dataset-root data/dataset_top \
  --restore-unreviewed-only
```

Then review as usual (restore also runs before the UI unless disabled):

```bash
python scripts/dataset_top_select/review_folder_placement.py \
  --dataset-root data/dataset_top \
  --splits train
```

Skip automatic restore:

```bash
python scripts/dataset_top_select/review_folder_placement.py \
  --dataset-root data/dataset_top \
  --no-restore-unreviewed
```

Only stems **not** in `reviewed[]` are moved back; manually reviewed images stay
in `images_reviewed/`.

## Resume

Progress is stored in:

`data/dataset_top/.review_folder_placement.json`

Each reviewed image is keyed by `(split, stem)` so re-runs skip completed items even after files were moved.

Moves are appended to:

`data/dataset_top/review_moves.log`

## Options

```bash
# Clear saved progress
python scripts/dataset_top_select/review_folder_placement.py --reset

# Review only train split
python scripts/dataset_top_select/review_folder_placement.py --splits train

# Custom state path
python scripts/dataset_top_select/review_folder_placement.py \
  --state-file /path/to/my_state.json
```

## Folders reviewed

- `images/train_top`, `images/train_oth`
- `images/val_top`, `images/val_other`
- `images/test_top`, `images/test_oth`

Matching `labels/` subfolders are moved together when a label file exists.
