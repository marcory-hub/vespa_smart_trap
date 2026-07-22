**One-line purpose:** migration plan + teach-me lesson track (Colab train, GCE VELA)
**Project ID:** `pt-vela` | **Bucket:** `pt-vela-gce` | **VM:** `vst-vela-01`
**Agent:** SoT for execution order | **Main Index:** [[__vespa_smart_trap]]
**Prompt source:** [[vst prompt to migrate colab to VM CGE]] | **Research:** [[vst research to migrate colab to VM CGE]]
**Runbook detail:** [[gcp-setup-pt-vela]]

---

# How to use this file (prompt + teach-me)

| Layer | File | Role |
| :--- | :--- | :--- |
| Scope | `vst prompt to migrate colab to VM CGE.md` | What the plan must cover (do not re-run unless scope changes) |
| Roadmap | **This file** | Phases, checkpoints, lesson order |
| Teaching | `@teach-me` + `teaching/MISSION.md` | One lesson per chat; **you run commands**; agent explains and checks |
| Facts | `gcp-setup-pt-vela.md` | CLI cheat sheet for Phase 1 |

**Fresh chat template:**

```text
@teach-me @notes/vst plan GCE VELA migration.md
Continue lesson [N]. I did [X]. Stuck at [Y] or ready for checkpoint.
Agent: teach only — do not run gcloud or change files unless I say apply.
```

---

# Teach-me progress

| Lesson | Topic | Status |
| :--- | :--- | :--- |
| 1 | GCP account, project, billing | done |
| 2 | APIs, T4 quota, gcloud install | done (quota: pending / approved) |
| 3 | GCS bucket + upload parity bundle | bucket done; upload: pending |
| 4 | Create VM + Jupyter tunnel | pending |
| 5 | Python 3.11 venv + pip pins on VM | pending |
| 6 | GCE notebook variant (no Colab APIs) | pending |
| 7 | Run VELA pipeline (500-calibration smoke) | pending |
| 8 | Full parity + GV2 handoff | pending |

Update **Status** in Obsidian after each lesson.

---

# 1. Executive summary

- **Training:** stays on Colab (`YOLO11n_training_2026_02_19.ipynb`).
- **VELA:** migrate `YOLO_pt_to_vela_2026_02_24.ipynb` to GCE before Colab runtime 2025.07 EOL (~2026-07).
- **Success:** `best_full_integer_quant_vela.tflite` ≤ 2.4 MB; parity with last Colab VELA run.
- **You operate GCP;** Cursor teaches steps. No W&B on GCE path.

---

# 2. Prerequisites

- Google account, billing linked to `pt-vela`
- T4 quota ≥ 1 in `europe-west4`
- Mac: `gcloud` + `gsutil` installed and authed
- Local bundle: `weights_dataset_for_GCE/best.pt`, `dataset.zip` (~1.2 GB)
- Calibration: notebook builds **500-image** subset from full dataset (not a separate `dataset_10.zip`)

---

# Lessons (you do; agent teaches)

## Lesson 1: GCP account and project — done

**You did:** project `pt-vela`, billing, deleted stray `test` project.

**Checkpoint:** `gcloud projects list` shows `pt-vela`.

---

## Lesson 2: APIs, quota, CLI — done

**You did:** Compute Engine + Cloud Storage APIs; T4 quota request; `gcloud auth login`.

**Checkpoint:** Quotas show T4 = 1 for `europe-west4` (approved).

**Concept:** Project **name** ≠ **project ID** (`pt-vela`).

---

## Lesson 3: Bucket and upload — in progress

**You do:**

```bash
export PROJECT_ID=pt-vela
export BUCKET=pt-vela-gce
gsutil cp weights_dataset_for_GCE/best.pt gs://${BUCKET}/input/
gsutil cp weights_dataset_for_GCE/dataset.zip gs://${BUCKET}/input/
gsutil ls -lh gs://${BUCKET}/input/
```

**Checkpoint:** two objects under `gs://pt-vela-gce/input/`.

**Concept:** GCS replaces Colab Google Drive.

---

## Lesson 4: VM + Jupyter

**You do:** create `vst-vela-01` per [[gcp-setup-pt-vela]] (after quota approved).

**Checkpoint:** `nvidia-smi` on VM shows T4; Jupyter at `http://localhost:8080` via SSH tunnel.

**Concept:** DLVM = Deep Learning VM image with PyTorch + Jupyter preinstalled.

---

## Lesson 5: Python 3.11 venv on VM

**You do:** pyenv or deadsnakes → venv 3.11; pip pins from research note (`tensorflow==2.18.0`, `onnx==1.17.0`, `kris-himax/ultralytics`, `ethos-u-vela`).

**Checkpoint:** `python --version` → 3.11.x inside venv.

**Concept:** DLVM default 3.12 is not parity with Colab 2025.07.

---

## Lesson 6: GCE notebook variant

**You do:** copy notebook to `YOLO_pt_to_vela_*_gce.ipynb` in submodule; replace `drive.mount`, `userdata`, `files.download` with `~/vst/` paths and `gsutil`.

**Checkpoint:** notebook opens in Jupyter; no `google.colab` imports.

**Agent teaches:** cell-by-cell diff; you edit or paste.

---

## Lesson 7: Smoke run

**You do:** pull `best.pt` + `dataset.zip` to `~/vst/`; run export + VELA (500-image calibration runs in notebook).

**Checkpoint:** `best_full_integer_quant_vela.tflite` exists; ≤ 2.4 MB; no OOM.

**Escalation:** OOM → `n1-standard-8` → `n1-highmem-8` (see research Addendum 6).

---

## Lesson 8: Full parity + GV2

**You do:**

```bash
gsutil cp gs://${BUCKET}/output/best_full_integer_quant_vela.tflite \
  gv2_firmware/model_zoo/tflm_yolo11_od/
```

Flash `@flash-gv2`; verify `@model-test` or UART INVOKE.

**Checkpoint:** metrics/size within expected delta vs last Colab VELA run.

**Rollback:** Colab notebook unchanged until sign-off.

---

# 3. GCE setup reference

See [[gcp-setup-pt-vela]] for commands. Defaults: `europe-west4-a`, `n1-standard-4` + T4, 100 GB disk.

---

# 4. Notebook changes (summary)

| Colab | GCE |
| :--- | :--- |
| `drive.mount` | skip; data in `~/vst/` from GCS |
| Drive paths for `dataset.zip`, `best.pt` | `gsutil cp` from `gs://pt-vela-gce/input/` |
| `files.download` | `gsutil cp` to bucket or laptop |
| Runtime 2025.07 | Python 3.11 venv |
| `num_images = 500` calibration | unchanged logic |

---

# 5. Risks

- T4 quota delay
- INT8 export OOM (escalate VM tier)
- Python/export chain sensitivity (stay on 3.11)
- Colab 2025.07 EOL ~2026-07

---

# 6. File touch list

| File | Action |
| :--- | :--- |
| `notes/vst plan GCE VELA migration.md` | this file; update lesson status |
| `notes/gcp-setup-pt-vela.md` | CLI runbook |
| `colab-notebooks/YOLO_pt_to_vela_*_gce.ipynb` | GCE variant (submodule) |
| `gv2_firmware/model_zoo/tflm_yolo11_od/` | deploy `*_vela.tflite` |

---

# 7. Timeline

| When | Milestone |
| :--- | :--- |
| 2026-06 | GCP project, bucket, VM, smoke |
| Before 2026-07 | Full parity; cutover from Colab VELA |
