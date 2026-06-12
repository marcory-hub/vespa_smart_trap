# VST common research topics

## When to mark needs research

| Signal | VST example |
| :--- | :--- |
| No SoT in repo or notes | GCE VM, GCS buckets, billing |
| User: "I don't know yet" | First GCP setup |
| Stale vs current stack | Colab runtime vs 2025.07 / Python 3.11 |
| Vendor behavior | T-SIM LTE AT commands, Himax toolkit |
| Migration spike | Colab → GCE training |

## Platform migration (Colab → GCE)

Research questions:

1. Which notebook steps (`YOLO11n_training_2026_02_19.ipynb`, `YOLO_pt_to_vela_2026_02_24.ipynb`) map to GCE vs stay on Colab?
2. GPU machine type and CUDA/driver pairing vs Colab experience?
3. Dataset: GCS layout vs local `gsutil rsync`; parity with Drive paths?
4. Secrets: service account vs user creds; no keys in repo?
5. Cost, idle shutdown, teardown?
6. Minimum parity test (short run, comparable metrics)?
7. Rollback to Colab if trial fails?

Deliverable must include: parity checklist, bootstrap commands, cutover, rollback, paste bullets.

**Out of scope unless user overrides:** local VELA on Mac; inference on T-SIM; YOLOv26.

## GCE greenfield

- VM type/GPU, region, image
- `gcloud` bootstrap, GCS mount vs `gsutil`
- Sync: GCE ↔ local ↔ Colab ↔ GV2
- Cost/teardown

## New hardware

- Datasheet vs `notes/_hardware_vst.md` pinout conflicts
- Bring-up tools, power, safety (LiPo, field)
- GV2 flash vs T-SIM sketch vs host-only

## Sources (check in order)

1. `notes/` paths from `project-context.mdc`
2. `scripts/`, `gv2_firmware/`, `notebooks/` (if synced)
3. `.cursor/rules/project-context.mdc`
4. Official vendor / Google Cloud docs
5. Web search with specific queries
