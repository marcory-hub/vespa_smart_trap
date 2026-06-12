---
name: model-test
description: Run or extend YOLO evaluation on GV2 with deployment threshold and slideshow benchmarks. Use when testing a model, benchmark inference, image_slider_web, or @model-test.
---

# Model test

Follow `.cursor/skills/read-notes/SKILL.md` for `notes/_model_vst.md` (active model, classes, deployment threshold).

Search `scripts/` before new utils. Deploy artifact: `int8_vela.tflite` only. Train/quant: `.cursor/skills/train-colab-vela/SKILL.md`.

## Modes

| Mode | Path |
| :--- | :--- |
| **Bench** | USB serial INVOKE + optional `scripts/image_slider_web/` camera feed |
| **Field trap** | T-SIM UART receiver; read `_hardware_vst.md`, not USB INVOKE |

## Evaluation

- Apply runtime `conf >=` threshold from `_model_vst.md`
- Log raw confidences when user asks for threshold sweeps
- Ground truth from benchmark filename rules; validate tensor shapes; flag SRAM if model nears GV2 limit

## Tools

| Script | Use |
| :--- | :--- |
| `scripts/image_slider_web/server.py` | Slideshow + GV2 camera pane |
| `scripts/gv2_yolomodel_test/benchmark_runner.py` | INVOKE benchmark, CSV, confusion matrix |
| `scripts/experiment_set_match/run_experiment.py` | Class-set serial experiment |

`source .venv/bin/activate` before running. See each folder README.

## Workflow

1. Confirm model flashed (`@flash-gv2` / skill verify)
2. Start slideshow if physical camera feed needed
3. Run script; cite output paths in report
4. Serial issues: `@uart-debug`

## Out of scope

- Flash (`@flash-gv2`)
- Dataset file renames (`.cursor/skills/dataset/SKILL.md`)
