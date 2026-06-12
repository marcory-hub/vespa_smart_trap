---
name: dataset
description: Work on YOLO datasets using notes and scripts/dataset_* tools. Use when the user asks about dataset counts, labels, train/val split, Roboflow, annotation, class names, or @dataset.
---

# Dataset

Follow `.cursor/skills/read-notes/SKILL.md` before any dataset fact (counts, versions, class list). Facts from notes and scripts only.

## Safety (non-negotiable)

- **Never rename** `.jpg` or `.txt` label files (pairing is by stem).
- Dry-run by default; scripts with `--apply` need backup first.
- **WARNING: Irreversible operation. Data loss risk.** before bulk delete, `rsync --delete`, or overwrite of `data/`.
- Do not commit `data/`, `notes/`, or credentials (see `@security-audit`).

## Before a new script

Search `scripts/dataset_*` and extend an existing tool if it fits. No new util without checking `scripts/` first.

| Folder | Purpose |
| :--- | :--- |
| `scripts/dataset_align_label_prefixes/` | Align `top_`/`oth_` label stems; train/val split; set `oth` class |
| `scripts/dataset_top_select/` | Review top vs other placement; build `dataset_top`; archive reviewed |
| `scripts/dataset_top_copy/` | Copy images/labels to splits; backfill missing top labels |
| `scripts/dataset_filter_classes/` | Filter classes (e.g. vvel, vcra, null) |
| `scripts/copied_pairs_review/` | Review duplicated pairs across dataset folders |

## Out of scope

- Local train, quant, or VELA (Colab `2025.07`, Python 3.11; cite `notebooks/*.ipynb`)
- Plain `int8.tflite` (use `int8_vela.tflite` on GV2)
- Inventing image counts, class IDs, or Roboflow project names

## Edits to notes

Agent suggests; user writes in Obsidian unless the user says apply to file. Counts and run history live in `notes/`, not in rules.
