# Vespa Smart Trap

**What:** *Vespa velutina* detector: YOLO11n on Grove Vision AI V2, dataset pipeline, Himax firmware integration, UART validation on ESP32-S3.

**Who:** Developers evaluating Cursor on constrained edge-AI stacks (multi-language repos, git submodules, ~2.4 MB NPU SRAM).

**Scope:** Model pipeline and GV2 firmware (this repo); trap mechanical design and LilyGO LTE (collaborators).

---

## In pictures

![3D-printed trap in the garden](../images/trap3DprintedModel.jpg)

![GV2 camera mount, lens facing down](../images/Cam-180CCW-final.jpg.jpeg)

![Live YOLO11n inference on GV2 (Himax toolkit)](../images/himax_output.png)

---

## Why this project exists

*Vespa velutina* is an invasive hornet. Worker hornets attack honey bee colonies. We need traps that spot a visit in the field, alert the beekeeper by SMS, and run on solar power at low cost per site.

Inference runs on the trap (Grove Vision AI V2). No video stream to the cloud.

---

## What runs where

| Stage | Where | Output |
| :--- | :--- | :--- |
| Capture | Camera in the trap | Raw images for labelling |
| Dataset | Local `scripts/` | Filtered YOLO labels, splits |
| Train | Colab (`yolo11n-on-grove-vision-ai-v2/`) | `*_full_integer_quant_vela.tflite` |
| Integrate | `gv2_firmware/` submodule (~2.4 MB SRAM) | Class map, flashable firmware |
| Bench test | GV2 UART -> ESP32-S3 (`esp_firmware/`) | JPEG + metadata on serial |
| Field unit | Custom PCB + LilyGO T-SIM7080G-S3 (target) | LTE alerts (collaborator) |

```text
Field images
    -> annotate (Grounding DINO) + verify pairs locally
    -> Colab: train YOLO11n, quantize, VELA
    -> gv2_firmware: post-processing, class labels, flash
    -> ESP32-S3: UART receiver, JPEG capture scripts
    -> LilyGO: LTE alerts (target)
```

---

## Dataset work with Cursor

**Problem:** 36,000 image/label pairs to filter, split, and verify.

**Cursor built in minutes:**

- `scripts/dataset_filter_classes/`: keep classes, rewrite YOLO labels
- `scripts/dataset_top_select/`: pick top-down images
- `scripts/copied_pairs_review/`: web UI to approve or reject pairs

**Result:** reliable dataset changes before Colab runs.

---

## Firmware with no documentation

**Problem:** Himax SDK hardcoded COCO classes at compile time. No docs for a hornet model.

**Cursor helped:**

- read `gv2_firmware/.../cvapp_yolo11n_ob.cpp`, traced the class map
- found hardcoded labels and output struct
- wrote the override in the submodule

**Then rules:** SRAM budget, correct `*_vela.tflite` artifact, "do not suggest" list for wrong platforms.

---

## Where Cursor needs rules (and a human)

1. **"Just use a Raspberry Pi."** Solar trap. Pi idles at 2W.

2. **"Try YOLOv8, it is well supported."** 2.4 MB NPU, custom VELA. Bold.

3. **It cannot touch the hardware.** No flash, no serial port, no loose UART wire. Still me.

4. **Rules are soft.** Submodule push/sync became `@` commands after repeated wrong-repo mistakes.

---

## Takeaways

1. **Useful at the edge:** dataset tooling, undocumented firmware, UART receivers.

2. **Rules and commands:** soft guardrails; submodules needed explicit `@` workflows.

3. **Human in the loop.** Not much vibing at the edge.
