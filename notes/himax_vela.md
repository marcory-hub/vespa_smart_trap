**One-line purpose:** 
**Short summary:**
**SoT:**
**Agent:** 
**Main Index:**

---

# Himax and Vela: chronology and reproducing yolo.pt → full quant vela.tflite

**One-line purpose:** Single chronological file of Himax and Vela work (Jun–Sep 2025) and steps to reproduce yolo.pt → full-integer-quant vela.tflite for Grove Vision AI V2.

**Goal:** Reproduce the pipeline: **YOLO .pt → int8 TFLite → Vela → int8_vela.tflite** (flash to GV2).

---

## Key info

| Item | Value |
|------|--------|
| **Working reference model** | `yolo11n_2025-09-01_224_e300_full_integer_quant_vela.tflite` (flashed successfully) |
| **GV2 format** | int8 TFLite compiled with **Vela** (Ethos-U55). Plain int8 TFLite not accepted. |
| **Size limit** | &lt;2.4 MB (docs also say ~2.1–2.4 MB; 256×256 model ~5.4 MB failed) |
| **Input size** | Square; max 240×240 in docs; YOLO uses multiples of 32. Used: 192 or 224. |
| **Flash address (YOLO11 OD)** | **0xB7B000** (offset 0x00000). Do not use 0x3AB7B000 for single-model flash. |
| **Vela** | ARM Ethos-U compiler; run **locally on macOS** (Vela does not work in Colab). |

Sources: [[gv2 modelvoorwaarden]], [[himax cli flash model]], [[himax_2025]].

---

## Chronological timeline (Jun–Sep 2025, from git and notes)

### 2025-07-12
- Added `acc-yolo-model-optimisation.mdc`. Image size 192 chosen (2^6; YOLO multiples of 32).

### 2025-07-24
- Vespa CV: flash YOLOv8, Grove Vision AI v2 deployment, SenseCraft, hardware notes.

### 2025-07-30
- **Himax:** New note `acc Himax yolov8n.md` (292 lines). Index and Grove Vision AI v2 renames.

### 2025-08-11 / 2025-08-12
- **Himax + Vela:** `acc Connect Grove Vision AI V2 to Himax.md`, `acc Firmware flash op mac mini m2.md`, `acc use HIMAX config file to generate vela model.md`, YOLO11n deployment steps, prune/quantize Colab.
- Reorg: `acc Himax yolov8n.md` removed; `acc Grove Vision AI V2 troubleshooting.md`, `acc firmware flashing.md` expanded; `acc grove vision ai v2 background info.md` added.
- Then: rename to `acc Connect to Himax.md`; "use HIMAX config file to generate vela model" removed; `acc CLI commands.md` added; large doc cleanup.

### 2025-08-16
- Flash Grove Vision AI v2; timeline and terminal output of flash attempts (Mac + Raspberry). Edge Impulse tested; issues (missing flash script, bootloader).

### 2025-08-23
- **Himax environment and model flashing:** [[himax environment]], [[himax build firmware image]], [[himax flash firmware first time]], [[himax makefile]], [[himax modelzoo readme]]. **Export:** [[yolov8n pt naar int8 vela tflite]] (export snippet + vela command).

### 2025-08-24
- **Vela / int8:** New/updated: `acc Himax AI web toolkit.md`, `acc Vela.md`, `acc Makefile met tflm_yolov8_od.md`, `acc makefile.md`, `acc modelzoo readme.md`, `acc yolov8n pt naar int8 vela tflite.md`, int8 192 vs 640, QAT, TFLite, Build/Flash firmware, Environment. Acc rules split.
- Performance drop by imgsz: [[z yolo issue performance drop TFLite YOLOv8 YOLO11]], [[yolov8n imgsz 192 vs 640]].

### 2025-08-25
- **Flash modelzoo:** yolov8_pose, yolo11_192, yolo11_224. Netron comparison (seeed vs custom). Vela .tflite notes; `acc CLI flash model.md`, `acc flash modellen uit modelzoo.md`.

### 2025-08-26
- **Himax:** Many notes moved under "Himax" (Build firmware, CLI, Environment, Flash, Makefile, modelzoo, troubleshooting). **Vela:** `acc Vela.md` expanded. YOLOv8n modelzoo format adaptation plan; PyTorch → full_integer_quant tflite; delete 4 transpose ops.

### 2025-08-29
- **Output index 1 out of range:** Custom YOLOv8n failed on GV2; single output `int8[1,8,756]` vs firmware expecting two outputs. DFL head; retrain without DFL recommended.

### 2025-08-30
- Conversion pt → onnx → TFLite → vela failed for yolov8n coco 80cls and vespCV. Open YOLO11_on_WE2_Tutorial.ipynb on Colab: module `imp` missing since Python 3.12.

### 2025-08-31
- **Himax CLI flash** and **pt to vela tflite** updated. YOLO11 on WE2, Colab; `acc yolo11 on we2 for PC on Colab.md`. Doc reorg (GV2 Documentatie).

### 2025-09-01
- **Himax:** "fix class names in himax"; `acc Himax CLI flash model.md`, `acc coco_classes fix.md`, `acc yolo11 224.md`. New: `acc_yolo11_pt_to_vela_2025-09-01.md`, `acc_yolo11 training 2025-09-01.md`. **Working model:** `yolo11n_2025-09-01_224_e300_full_integer_quant_vela.tflite`.

### 2025-09-02
- **YOLO11 imgsz224:** [[yolo11n_25-09-01a_224_e300]] best. 256×256 test → no detection; buffer resize error (model too large).

### 2025-09-03
- **Himax:** `acc Himax CLI flash model.md` extended. **Vela:** `acc yolo11_pt_to_vela_2025-09-01.md`; experiment 256 px; YOLO11 training 224 e300, e300 b512; timeline and planning.

### 2025-09-04
- Colab requirements (vela in repo).

---

## Reproduction pipeline: yolo.pt → full quant vela.tflite

### 1. Model and GV2 constraints
- **Format:** int8 TFLite, then **Vela**-compiled. GV2 only runs `int8_vela.tflite`.
- **Size:** Output vela .tflite &lt;2.4 MB.
- **Input:** Square, e.g. 192×192 or 224×224 (multiples of 32). Max 240×240 in docs.
- **Classes:** Match class list in Himax AI Web Toolkit (see [[himax coco_classes fix]]; `cvapp_yolo11_ob.cpp`, toolkit JS).

### 2. Export .pt → int8 TFLite (Colab or local)

From git-recovered note (Aug 2025) and [[himax_2025]], [[himax vela]]:

```python
from ultralytics import YOLO

model = YOLO("best.pt")
image_size = 192  # or 224 to match training
model.export(format="tflite", imgsz=image_size, int8=True, data="jouw_dataset.yaml")
```

**Full-integer quantization** (from notes): use `data` yaml for calibration, and optionally:
- `fraction=1.0` (e.g. [[z yolo qat quantization aware training]])
- `simplify=True`; for YOLO11n, `nms=False` can help Vela compatibility ([[himax vela]])

**YOLO11:** The 2025-09-01 run used the **YOLO11_on_WE2** ultralytics fork in Colab ([[himax_2025]]). Colab notebook from that period is not in this repo; pipeline is reconstructed from notes and Himax/Seeed WE2 docs.

**YOLO11n transpose issue:** Default YOLO11n TFLite can contain TRANSPOSE ops Vela does not support. If Vela fails, use YOLOv8n export (better compatibility) or the YOLOv8_on_WE2 / YOLO11_on_WE2 flow that removes or replaces transpose ops ([[gv2 documentation]], [[himax vela]]).

### 3. Run Vela (local macOS only)

**Install:**
```bash
pip install ethos-u-vela
```
If needed (numpy/API issues): [[vela.tflite]] documents pinning numpy and setuptools_scm before installing.

**Config:**
- Seeed: [[vela_config.ini]]
- Project path referenced in notes: `zz_vespa_smart_trap/cv_vespcv_grovevisionaiv2/himax/himax_vela.ini` (if present in your project).
- Alternative snippet: [[himax vela]] (Alternative Vela Config).
- Refs: [[ML_FVP_EVALUATION]], [[YOLOv8_on_WE2]].

**Command (input file last):**
```bash
vela path/to/your_int8.tflite \
    --accelerator-config ethos-u55-64 \
    --config himax_vela.ini \
    --system-config My_Sys_Cfg \
    --memory-mode My_Mem_Mode_Parent \
    --output-dir output/
```
Compiled model appears in `output/`. Copy to `model_zoo/tflm_yolo11_od/` for flashing.

**Simpler variant** (from [[vela.tflite]]):  
`vela your_int8_model.tflite --config ethos-u55 --outdir ./grove_output`

### 4. Flash to GV2
See [[himax cli flash model]], [[himax flash firmware first time]], [[gv2 build, copy, regenerate and flash]]. Summary:
- Build firmware with `APP_TYPE = tflm_yolo11_od`; generate image; use xmodem to send `output.img` and model with address **0xB7B000 0x00000**.

---

## Vela compatibility (YOLO11n)

From [[himax vela]]:

- **TRANSPOSE:** YOLO11n can have TRANSPOSE patterns Vela does not support (e.g. `[0 1 3 2]`, `[0 3 1 2]`, `[0 2 3 1]`). Vela supports only a subset of 4D transposes.
- **Non-constant weights:** FULLY_CONNECTED with non-constant weight tensors can block NPU acceleration.
- **IndexError:** Can occur during Vela graph rewriting.

**Workarounds:** Prefer YOLOv8n export for Vela; or use YOLO11n with `nms=False` and `simplify=True`; or follow ONNX-simplify → onnx2tf → TFLite path in [[himax vela]]. For YOLOv8n, [[YOLOv8_on_WE2]] documents export to int8 TFLite and **deleting 4 transpose ops** for WE2.

---

## Environment (macOS, Apple Silicon)

From [[himax environment]], [[himax_2025]]:
- **Python:** venv in Himax project; xmodem deps: `pip install -r xmodem/requirements.txt`.
- **Make:** GNU make (`brew install make`; use `gmake` or `alias make='gmake'`).
- **ARM GNU Toolchain:** 14.3 for arm64. Path: `/Applications/ArmGNUToolchain/14.3.rel1/arm-none-eabi/bin`; set in Makefile as `GNU_TOOLPATH` and/or in PATH.

---

## References in this repo

| Topic | Note |
|--------|------|
| Flash commands | [[himax cli flash model]], [[himax cli flash yolo11n model]] |
| Build & image gen | [[himax build firmware image]], [[gv2 build, copy, regenerate and flash]] |
| Environment & make | [[himax environment]], [[himax makefile]], [[himax makefile met tflm_yolov8_od]] |
| GV2 constraints | [[gv2 modelvoorwaarden]], [[himax gv2 troubleshooting]] |
| Vela & export | [[himax vela]], [[vela.tflite]], [[himax_2025]] |
| YOLO11 training (2025-09-01) | [[yolo11n_25-09-01a_224_e300_colab]], [[yolo11n_25-09-01a_224_e300]] |
| Timeline Jul–Sep 25 | [[z_vespa_smart_trap/z model timeline 2025-07 - 2025-09]] |
| GV2 / WE2 docs | [[gv2 documentation]] |

---

## Open points / clarifying questions

1. **himax_vela.ini contents:** The exact file is referenced at `zz_vespa_smart_trap/cv_vespcv_grovevisionaiv2/himax/himax_vela.ini` and in .gitignore. If missing locally, use Seeed [[vela_config.ini]] or the snippet in [[himax vela]].
2. **Exact 2025-09-01 export:** The Colab notebook that produced the working model is not in this repo. Confirmed: full integer quant, imgsz 224, same classes as current use; optional `fraction=1.0`, `simplify=True`, and possibly YOLO11_on_WE2 fork or transpose handling. Reconstruct and re-run export + Vela, then document the exact commands here.
3. **YOLO11n vs YOLOv8n:** If Vela fails on YOLO11n, use YOLOv8n export or the YOLOv8_on_WE2 “delete 4 transpose ops” flow; for YOLO11n, confirm whether a WE2 fork or custom export was used for the 2025-09-01 model.
4. **Ultralytics version:** Notes mention 8.3.166 for training; YOLO11_on_WE2 fork version used in Colab for export is not pinned here.

---

*Once the exact export and vela commands are confirmed on a new run, add them to the "Reproduction pipeline" section so this note is the single guide for yolo.pt → full quant vela.tflite.*
