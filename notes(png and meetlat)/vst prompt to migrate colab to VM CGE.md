**One-line purpose:** prompt for migration made by cursor
**Short summary:** migration from colab to GCE
**Agent:** SoT
**Main Index:** [[__vespa_smart_trap]]
Previous: [[vst research to migrate colab to VM CGE]]

---
# VST plan prompt: Colab → GCE (VELA only)

**Cursor Plan mode. Output one plan markdown file. No implementation in this chat.**

---

## Task

Produce a **plan markdown file** for migrating **`YOLO_pt_to_vela_2026_02_24.ipynb`** to user-owned GCE. Training stays on Colab (`YOLO11n_training_2026_02_19.ipynb`).

The plan must cover three phases in order:

1. **Set up GCE** (GCP project, billing, T4 quota, GCS, minimum VM, JupyterLab).
2. **Implement the GCE notebook** (adapter variant in GitHub SoT; no `google.colab.*`).
3. **Run the pipeline** on GCE: `best.pt` + calibration dataset → `best_full_integer_quant_vela.tflite` (≤ 2.4 MB) → download → GV2 flash path.

Target: parity before Colab runtime **2025.07** EOL (~2026-07).

---

## Mode

**Plan only.** Deliver `notes/vst plan GCE VELA migration.md` (or equivalent name under `notes/`). No file edits in this chat except the plan output the user saves.

---

## Background

- **Why migrate VELA:** Colab runtime 2025.07 retirement (~2026-07). Cost research (Addendum 4): training stays Colab (~5 to 10× cheaper T4).
- **W&B:** Colab training only. **No W&B on GCE VELA path.**
- **Rollback:** Colab notebooks unchanged until GCE VELA parity signed off.

---

## Parity inputs (exact paths)

Large files are gitignored and cursorignored. Do not index; reference by path only.

| File | Absolute path |
| :--- | :--- |
| Weights | `/Users/md/Developer/vespa_smart_trap/weights_dataset_for_GCE/best.pt` |
| Full dataset | `/Users/md/Developer/vespa_smart_trap/weights_dataset_for_GCE/dataset.zip` |
| Smoke dataset (10 images) | `/Users/md/Developer/vespa_smart_trap/weights_dataset_for_GCE/dataset_10.zip` |

Upload all present files to `gs://BUCKET/input/` before the VM run. On VM: `~/vst/best.pt`, unzip to `~/vst/dataset/` (full) or `~/vst/dataset_10/` (smoke).

Provenance `[to be verified]`: W&B run `yolo11n_top_e300_b395` (`vst_2026-05_top`).

---

## Verification (no training epochs)

VELA has **no training epochs**. Do not plan 10-epoch smoke.

| Phase | Input | Pass criteria |
| :--- | :--- | :--- |
| **Smoke** | `best.pt` + **10-image** `dataset_10.zip` for INT8 calibration | Export + VELA completes; output ≤ 2.4 MB; no OOM |
| **Full parity** | `best.pt` + full `dataset.zip` | `best_full_integer_quant_vela.tflite` ≤ 2.4 MB; size/metrics vs last Colab VELA run |

Smoke validates the export chain cheaply before full-dataset parity.

---

## Minimum GCE VM (VELA-only)

Plan must default to **minimum viable** shape, with escalation steps if OOM.

| Tier | Shape | Disk | When |
| :--- | :--- | :--- | :--- |
| **Default minimum** | `n1-standard-4` + 1× T4, `europe-west4-a` | 100 GB | 10-image smoke + VELA |
| **Step up** | `n1-standard-8` + T4 | 100 GB | INT8 export OOM on standard-4 |
| **Last resort** | `n1-highmem-8` + T4 | 100 GB | TF/onnx2tf still OOM |

- **Instance name:** `vst-vela-01` (general; not date-locked). Optional alias `cv2026-06` for first trial only.
- **Image:** `pytorch-2-9-cu129-ubuntu-2204-nvidia-580`, `install-nvidia-driver=True`.
- **Jupyter:** `gcloud compute ssh jupyter@vst-vela-01 -- -L 8080:127.0.0.1:8080`
- **Python:** 3.11 venv (pyenv or deadsnakes); not DLVM default 3.12.
- **Cost control:** stop VM when idle; document teardown.

On-demand EU estimate: **~$0.25 to 0.35/hr** for `n1-standard-4` + T4 vs **~$1.10/hr** for highmem (Addendum 4).

---

## GV2 handoff (download artifact)

Plan must include post-run steps:

1. GCE output: `best_full_integer_quant_vela.tflite` (notebook naming).
2. Upload to GCS output prefix, then download to laptop:

```bash
gsutil cp gs://${BUCKET}/output/best_full_integer_quant_vela.tflite \
  gv2_firmware/model_zoo/tflm_yolo11_od/
```

3. Flash via `@flash-gv2` (921600 baud; model slot per `README.md`).
4. Verify with `@model-test` or UART INVOKE.

Deploy name follows existing convention (`*_full_integer_quant_vela.tflite` in `model_zoo/tflm_yolo11_od/`). Do not use raw `int8.tflite`.

---

## Software

- **Notebook SoT:** `marcory-hub/Seeed_Grove_Vision_AI_Module_V2` `main`; sync via `@sync-colab-notebooks`.
- **Deliverable (notebook):** GCE variant e.g. `YOLO_pt_to_vela_2026_02_24_gce.ipynb` with top adapter cell (`~/vst/`, GCS paths, no Colab APIs).
- **VELA stack:** `kris-himax/ultralytics`, `tensorflow==2.18.0`, `onnx==1.17.0`, `onnxruntime==1.26.0`, `ethos-u-vela`, `himax_vela.ini`, `no_post=True`, `imgsz=224`.
- **3.12:** pin `tflite_support<=0.4.3` if 3.12 ever tested (Addendum 3).

---

## Bootstrap sketch (plan must expand)

```bash
export PROJECT_ID=YOUR_PROJECT_ID
gcloud config set project ${PROJECT_ID}

export REGION=europe-west4
export ZONE=europe-west4-a
export BUCKET=vst-artifacts-${PROJECT_ID}
export INSTANCE_NAME=vst-vela-01

gsutil cp weights_dataset_for_GCE/best.pt gs://${BUCKET}/input/
gsutil cp weights_dataset_for_GCE/dataset_10.zip gs://${BUCKET}/input/
gsutil cp weights_dataset_for_GCE/dataset.zip gs://${BUCKET}/input/

gcloud compute instances create ${INSTANCE_NAME} \
  --zone=${ZONE} \
  --machine-type=n1-standard-4 \
  --image-family=pytorch-2-9-cu129-ubuntu-2204-nvidia-580 \
  --image-project=deeplearning-platform-release \
  --maintenance-policy=TERMINATE \
  --accelerator="type=nvidia-tesla-t4,count=1" \
  --boot-disk-size=100GB \
  --metadata="install-nvidia-driver=True"
```

Full bootstrap: research note (bootstrap steps 7 to 8 include `best.pt` on VM).

---

## Context attachments

**Required:**

```
@.cursor/rules/project-context.mdc
@.cursor/rules/safety-guardrails.mdc
@.cursor/rules/global-rules.mdc
@.cursor/rules/agent-persona.mdc
@vst research to migrate colab to VM CGE.md
@.cursor/commands/sync-colab-notebooks
```

**If needed:**

```
@notes/_hardware_vst.md
@notes/_model_vst.md
@.cursor/commands/flash-gv2
@.cursor/skills/model-test/SKILL.md
```

Do **not** attach `weights_dataset_for_GCE/` (cursorignored). Use exact paths in table above.

---

## Plan output structure

The plan markdown must include:

1. Executive summary (Colab train + GCE VELA split).
2. Prerequisites (GCP account, billing, T4 quota wait).
3. GCE setup (bucket layout, VM create, Jupyter tunnel, 3.11 venv, pip pins).
4. Notebook implementation (cells to change, GCE variant location, 10-image calibration parameter).
5. Execution order (smoke with `dataset_10.zip`, then full parity with `dataset.zip`).
6. GV2 handoff (gsutil download, `model_zoo` path, flash, verify).
7. Parity checklist and rollback.
8. Risks (Addendum 3 export chain, OOM escalation, quota delay).
9. File touch list (notes runbook, GCE notebook in submodule).
10. Timeline to 2026-07 EOL.

---

## Non-goals

- GCE training migration.
- W&B on VELA path.
- Local Mac as primary path.
- Colab frontend + GCE backend hybrid.
- Inference on T-SIM.

---

## Resolved defaults

| Topic | Default |
| :--- | :--- |
| Region | EU `europe-west4-a` |
| Scope | VELA notebook only on GCE |
| Deliverable | Plan md + GCE notebook variant + `notes/` runbook |
| VM | `n1-standard-4` + T4 minimum; escalate on OOM |
| Instance | `vst-vela-01` |

---

## After plan is saved

Obsidian sync → optional `@grill-me` on plan.

**Teach-me path (preferred):** `@teach-me` + `@notes/vst plan GCE VELA migration.md` — one lesson per chat; user runs commands; agent teaches and checks checkpoints. Update lesson status in plan. CLI detail: `gcp-setup-pt-vela.md`.

Implementation by agent only when user says apply.
