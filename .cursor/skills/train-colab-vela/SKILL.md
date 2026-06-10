---
name: train-colab-vela
description: Guides Colab train and PT to int8_vela quant for GV2. Use when Colab training, VELA, quantize tflite, int8_vela, or @train-colab-vela.
---

# Train and quant (Colab)

**No local train, quant, or VELA** (`project-context.mdc`). Colab runtime `2025.07`, Python 3.11.

## Before cells

1. `@sync-colab-notebooks` so agent cites real notebook paths under `colab-notebooks/`
2. `.cursor/skills/read-notes/SKILL.md` for `notes/_model_vst.md`, `notes/swift-yolo documentation.md`
3. SoT repo: `https://github.com/marcory-hub/Seeed_Grove_Vision_AI_Module_V2` branch `main`

## Artifact rules

- Deploy to GV2: `int8_vela.tflite` only (not plain `int8.tflite`)
- YOLO11n; resolution per `notes/_hardware_vst.md`
- No YOLOv26

## Workflow

1. Train in Colab notebook (user runs cells)
2. Export full-integer quant TFLite per Himax notebook blocks
3. Run VELA compile step; output filename ends with `_vela.tflite`
4. Copy artifact to `gv2_firmware/model_zoo/` path user specifies; flash via `@flash-gv2`

## Agent role

- Debug Colab errors from user paste or notebook Read after sync
- Do not invent cell contents; read `colab-notebooks/*.ipynb` or linked GitHub
- After new model: offer `@flash-gv2` and `@model-test`

## Out of scope

- Local `.venv` quant on Mac unless user explicitly overrides project rule
- Dataset prep (`.cursor/skills/dataset/SKILL.md`)
