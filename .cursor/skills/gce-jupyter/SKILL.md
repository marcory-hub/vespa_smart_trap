---
name: gce-jupyter
description: Start Jupyter on vst-vela-01, SSH tunnel from Mac, and verify VELA notebook smoke. Use when GCE notebook, Jupyter tunnel, vst-vela-01 browser, or @gce-jupyter.
---

# GCE Jupyter (judgment)

**Run steps (full workflow, step 0 onward):** `.cursor/commands/gce-jupyter` via `@gce-jupyter`.

**Migration plan:** `notes/vst plan GCE VELA migration.md`.

## When to use

- Lesson 6–7: edit or run `YOLO_pt_to_vela_2026_02_24_gce.ipynb`
- User closed all terminals or lost Jupyter/tunnel
- User reports `ERR_CONNECTION_REFUSED` on Jupyter URL
- Handoff mentions Jupyter up/down or tunnel port

## Agent role

**Default (operator):** run `scripts/gce_vela/remote.sh` from the Mac repo root via the agent Shell tool. Stream output in the agent terminal; read `scripts/gce_vela/outputs/*/remote.log` and `remote.sh pull-log`. Do **not** paste `remote.sh` / `gcloud` commands for the user to run. Do **not** ask the user to paste errors unless SSH or `gcloud` is unavailable on the agent shell.

**Teach mode (`@teach-me`):** one checkpoint per turn; user runs the single command shown for that step.

**Jupyter (optional):** `@gce-jupyter` when the user wants Chrome/Lab. Three-terminal order (VM Jupyter → Mac tunnel → Chrome). Label **Mac** (`md@m2`) vs **VM** (`md@vst-vela-01`).

**Terminal runner:** `@gce-run` → `.cursor/commands/gce-run` + `scripts/gce_vela/vm_run.py` (mirrors notebook steps).

## Notebook checks (static, Mac)

```sh
ls -lh notebooks/YOLO_pt_to_vela_2026_02_24_gce.ipynb
grep -E 'google\.colab|drive\.mount|/content/|files\.download' notebooks/YOLO_pt_to_vela_2026_02_24_gce.ipynb
# pass: no output
```

## Escalation

| Issue | Action |
| :--- | :--- |
| VM STOPPED | `gcloud compute instances start` |
| OOM on export | Plan addendum: `n1-standard-8` then `n1-highmem-8` |
| Quota / GPU | User checks Console; VELA export is mostly CPU |
| Artifact | `gs://pt-vela-gce/output/` then `@flash-gv2` |

## Out of scope

- Colab training (`YOLO11n_training_2026_02_19.ipynb` stays on Colab)
- Editing `notebooks/*.ipynb` unless user says apply
