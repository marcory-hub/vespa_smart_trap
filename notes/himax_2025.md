**One-line purpose:** 
**Short summary:**
**SoT:**
**Agent:** 
**Main Index:**

---
# Himax method: flash YOLO11n to Grove Vision AI V2 (2025–2026)

**One-line purpose:** Step-by-step recap of what worked in July–Sept 2025 to flash a YOLO11n model to GV2, and how to repeat it for a new .pt model.

**Reference model that worked:** `yolo11n_2025-09-01_224_e300_full_integer_quant_vela.tflite` (flashed successfully; see [[himax cli flash model]], [[gv2 flash model windows version]]).

---

## Current setup (2026)

- **New .pt to convert:**  
  `/Users/md/Developer/cv_vespa_modellen/_yolo11n_vespa_2026-02v1_60px_e300_b395_imgsz192/weights/best.pt`  
  Same classes as the 2025-09-01 model → no change needed in Himax AI toolkit or `cvapp_yolo11_ob.cpp`.
- **Archive / reference SDK:** Seeed_Grove_Vision_AI_Module_V2 (HimaxWiseEyePlus repo or your local clone). Use it for build, flash, and `model_zoo/tflm_yolo11_od/` layout.
- **Export pipeline:** The Colab notebook used in July–Sept 2025 is not available. The steps .pt → int8 TFLite → int8_vela.tflite must be reconstructed from Himax/Seeed WE2 docs and the notes in section 8.

---

## 1. Model requirements (GV2)

From [[gv2 modelvoorwaarden]], [[himax gv2 troubleshooting]]:

- **Format:** TFLite INT8 quantized, compiled with **Vela** (Ethos-U55). GV2 only supports `int8_vela.tflite`; plain `int8.tflite` is not acceptable. .pt cannot run on GV2; convert via **int8 TFLite** → **int8_vela.tflite**.
- **Size:** Your context: new YOLO11n .pt is 5.5 GB; GV2 model partition is 2.4 GB; a 2.1 GB int8_vela.tflite is proven to work. Target: produce an int8_vela.tflite that fits the partition (e.g. in the 2.1–2.4 GB range).  
  Note: In this repo’s notes and Seeed wiki, the limit is also stated as **&lt;2.4 MB** (megabytes); if your device/docs use MB, the target is ~2.1–2.4 MB.
- **Input:** Square; max 240×240 in docs; YOLO uses multiples of 32. Your new model is trained at **imgsz192**; the 2025-09-01 reference was 224×224. Use 192 for consistency with training.
- **Flash address for YOLO11 OD:** Use **0xB7B000** (and offset 0x00000). Do **not** use 0x3AB7B000 for the single-model flash ([[himax cli flash model]]).

---

## 2. Environment (macOS, Apple Silicon)

From [[himax environment]], [[himax build firmware image]]:

- **Python:** Use a venv in the Himax project folder; install xmodem deps there (`pip install -r xmodem/requirements.txt`).
- **Make:** Must be **GNU make**. On macOS: `brew install make`, then use `gmake` or `alias make='gmake'`.
- **ARM GNU Toolchain (Apple Silicon):** Use **14.3** for arm64 (not 13.2 x86). Install from: [arm-gnu-toolchain-14.3.rel1-darwin-arm64-arm-none-eabi.pkg](https://developer.arm.com/-/media/Files/downloads/gnu/14.3.rel1/binrel/arm-gnu-toolchain-14.3.rel1-darwin-arm64-arm-none-eabi.pkg). Default path: `/Applications/ArmGNUToolchain/14.3.rel1/arm-none-eabi/bin`.
- **PATH:**  
  `export PATH="/Applications/ArmGNUToolchain/14.3.rel1/arm-none-eabi/bin:$PATH"`  
  (and optionally the same in `~/.zshrc`). Run `hash -r` after changing PATH.
- **Check:**  
  `which arm-none-eabi-gcc` → should point to the 14.3 path.  
  `echo "int main() { return 0; }" | arm-none-eabi-gcc --specs=nano.specs -x c -c -o /dev/null -` → no output means OK.
- **Optional in Makefile:** In `EPII_CM55M_APP_S/Makefile` you can set  
  `GNU_TOOLPATH ?= /Applications/ArmGNUToolchain/14.3.rel1/arm-none-eabi/bin`  
  so the build always uses this toolchain.

---

## 3. Clone and set app type (YOLO11 OD)

From [[himax build firmware image]], [[himax makefile met tflm_yolov8_od]], [[gv2 flash model windows version]]:

- Clone (with submodules):  
  `git clone --recursive https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2.git`  
  then `cd Seeed_Grove_Vision_AI_Module_V2`.

- Set **APP_TYPE** for YOLO11 object detection:  
  In `EPII_CM55M_APP_S/Makefile`, at the bottom, set:  
  `APP_TYPE = tflm_yolo11_od`  
  (not `tflm_yolov8_od` or `allon_sensor_tflm`).

---

## 4. Build firmware image (macOS)

From [[himax build firmware image]], [[himax cli flash model]], [[gv2 build, copy, regenerate and flash]]:

```sh
# Use your clone of Seeed_Grove_Vision_AI_Module_V2 (archive/reference version)
cd /path/to/Seeed_Grove_Vision_AI_Module_V2
source .venv/bin/activate
export PATH="/Applications/ArmGNUToolchain/14.3.rel1/arm-none-eabi/bin:$PATH"
hash -r

cd EPII_CM55M_APP_S
make clean
make
```

- Output ELF:  
  `obj_epii_evb_icv30_bdv10/gnu_epii_evb_WLCSP65/EPII_CM55M_gnu_epii_evb_WLCSP65_s.elf`

Then generate the firmware image (macOS arm64):

```sh
cd ../we2_image_gen_local/
cp ../EPII_CM55M_APP_S/obj_epii_evb_icv30_bdv10/gnu_epii_evb_WLCSP65/EPII_CM55M_gnu_epii_evb_WLCSP65_s.elf input_case1_secboot/
./we2_local_image_gen_macOS_arm64 project_case1_blp_wlcsp.json
```

- Output image: `output_case1_sec_wlcsp/output.img`

---

## 5. Put your vela model in model_zoo

- Copy your **int8 Vela-compiled** `.tflite` into:  
  `model_zoo/tflm_yolo11_od/`  
  (e.g. name it like `yolo11n_2026_02_192_full_integer_quant_vela.tflite`).
- Ensure file size is **&lt;2.4 MB**.

---

## 6. Flash firmware and model to GV2

From [[himax cli flash model]], [[himax flash firmware]], [[gv2 build, copy, regenerate and flash]]:

- Install xmodem (in the same venv):  
  `pip install -r xmodem/requirements.txt`

- Find port:  
  `ls /dev/tty.*` or `ls /dev/cu.usbmodem*`  
  On macOS both `cu.usbmodem*` and `tty.usbmodem*` are used in notes; if one fails, try the other.

- Permissions (if needed):  
  `sudo chmod 666 /dev/tty.usbmodem58FA1047631`  
  (replace with your port).

- **Flash firmware only (optional check):**  
  `python3 xmodem/xmodem_send.py --port=YOUR_PORT --baudrate=921600 --protocol=xmodem --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img`

- **Flash firmware + YOLO11 model (what worked for the 2025-09-01 model):**

```sh
cd /path/to/Seeed_Grove_Vision_AI_Module_V2
source .venv/bin/activate

python3 xmodem/xmodem_send.py \
  --port=/dev/tty.usbmodem58FA1047631 \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img \
  --model="model_zoo/tflm_yolo11_od/yolo11n_2025-09-01_224_e300_full_integer_quant_vela.tflite 0xB7B000 0x00000"
```

- Replace the model filename with your new vela `.tflite` if needed.  
- Replace the port with your actual device (e.g. `/dev/cu.usbmodem58FA1047631` if that is what works on your Mac).

- When prompted, **press the black reset button** on the GV2. When you see  
  `Do you want to end file transmission and reboot system? (y)`  
  answer and let it finish; then the device should run with the new model.

---

## 7. Verify with Himax AI Web Toolkit

From [[gv2 flash model windows version]], [[himax ai web toolkit installation]]:

- Download:  
  [Himax_AI_web_toolkit.zip](https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2/releases/download/v1.1/Himax_AI_web_toolkit.zip)  
  (or use a local copy if you have one with custom class names).
- Open `index.html` in a browser, select Grove Vision AI V2, connect to the same serial port (e.g. 921600 bps), and check that detections appear. If you use custom classes, ensure the toolkit’s class list matches your model (see [[himax coco_classes fix]]).

---

## 8. Export pipeline: .pt → int8 TFLite → Vela (reconstruct from docs)

The Colab notebook used in July–Sept 2025 is not available. **Split:** do .pt → int8 TFLite in Colab (or locally with Ultralytics); **run Vela locally on macOS** (Vela does not work in Colab). The following is inferred from this repo’s notes and Himax/Seeed WE2 docs.

**Input .pt for 2026 run:**  
`/Users/md/Developer/cv_vespa_modellen/_yolo11n_vespa_2026-02v1_60px_e300_b395_imgsz192/weights/best.pt`  
Trained at **imgsz 192**; same classes as 2025-09-01.

### Recovered pipeline (from READ_ONLY, 410 vespa velutina cv)

The following steps were found in **READ_ONLY/400 computer vision/410 vespa velutina cv/nolink/** (do not edit that folder). Use them as the reference for how int8_vela.tflite was produced in 2025.

**Source files:**  
- `acc yolov8n pt naar int8 vela tflite.md` — export snippet and vela command  
- `acc yolo11n pt to vela requirements.md` — Colab env with `ultralytics @ file:///content/YOLO11_on_WE2/ultralytics`

**Step 1 — Export .pt → int8 TFLite** (Colab or local; for YOLO11n the requirements show the **YOLO11_on_WE2** ultralytics fork was used in Colab):
```python
from ultralytics import YOLO
model = YOLO("best.pt")
image_size = 192  # or 224 to match training
model.export(format="tflite", imgsz=image_size, int8=True, data="jouw_dataset.yaml")
```
Use your `data.yaml` (e.g. from the dataset used for training) for calibration. For the 2026 model use `imgsz=192` and the dataset yaml that matches `best.pt`.

**Step 2 — Vela** (local macOS; Vela reference in the old note: [HimaxWiseEyePlus/ML_FVP_EVALUATION](https://github.com/HimaxWiseEyePlus/ML_FVP_EVALUATION)):
```bash
pip install ethos-u-vela
vela --accelerator-config ethos-u55-64 --config himax_vela.ini --system-config My_Sys_Cfg --memory-mode My_Mem_Mode_Parent --output-dir ./img_yolov8_192 ./img_yolov8_192/yolov8n_full_integer_quant_size_192.tflite
```
So: **input file last**; `--output-dir` is the directory where the compiled model will be written. Replace the input path with your int8 `.tflite` and the output dir with a folder of your choice (e.g. `./output_vela`). Config: use `zz_vespa_smart_trap/cv_vespcv_grovevisionaiv2/himax/himax_vela.ini` as in subsection "Run Vela locally" below.

**Note:** The old note uses YOLOv8n naming (`yolov8n_full_integer_quant_size_192.tflite`); for YOLO11n the export produces a similar int8 TFLite, then the same vela command applies. If YOLO11n export produces unsupported transpose ops, see [[himax vela]] and the YOLOv8_on_WE2 / YOLO11_on_WE2 transpose-removal flow.

### Training (reference, 2025-09-01)

- Training for the 2025-09-01 model is in [[yolo11n_25-09-01a_224_e300_colab]]: YOLO11n, 224×224, 300 epochs, output e.g. in `vespCV_acc`. The export started from **best.pt** from that run.

### Export to TFLite (inferred)

- Ultralytics export with **full integer quantization** and **fraction=1.0** is referenced in notes (e.g. [[z_vespa_smart_trap/z yolo qat quantization aware training]]: `model.export(format='tflite', int8=True, fraction=1.0, data='data.yaml')`).
- For YOLO11, TFLite export can have **TRANSPOSE** ops that Vela does not support ([[himax vela]]). The YOLOv8_on_WE2 repo documents exporting YOLOv8n to int8 TFLite and **deleting 4 transpose ops** for WE2; a similar or adapted flow may have been used for YOLO11n ([[gv2 documentation]]).
- The notes also refer to a **post-processing (box decoding) separation** to reduce accuracy drop ([[z_vespa_smart_trap/z yolo issue performance drop TFLite YOLOv8 YOLO11]]); that may be part of a fork or custom export (e.g. DeGirum/ultralytics or a Himax/WE2 notebook).

So a plausible pipeline is:

1. **Export .pt → int8 TFLite** (with `data.yaml` for calibration):  
   For the 2026 model use **imgsz=192** to match training. e.g. `model.export(format='tflite', int8=True, imgsz=192, data='data.yaml', fraction=1.0, simplify=True)` (and possibly `nms=False` or a custom export from YOLO11_on_WE2 / YOLOv8_on_WE2).
2. **Optional:** If the TFLite has unsupported transpose patterns, apply the transpose-removal or conversion steps from the Himax/Seeed WE2 docs or notebook (exact steps not in this repo).
3. **Vela:** Compile the int8 TFLite with the Ethos-U55 Vela config — **run Vela locally** (Vela does not work in Colab). See subsection below.

### Run Vela locally (macOS)

Vela is the ARM Ethos-U compiler; it runs on macOS and is the step that produces `int8_vela.tflite` from an int8 TFLite. Do the **.pt → int8 TFLite** step in Colab (or locally with Ultralytics), then run **Vela on your Mac**.

1. **Install Vela** (in a venv, or the same one you use for the Himax SDK):
   ```bash
   pip install ethos-u-vela
   ```
   Optional: pin a version, e.g. `pip install ethos-u-vela==3.12.0` if needed for compatibility.

2. **Config file:** Use the project’s local config (matches `My_Sys_Cfg` and `My_Mem_Mode_Parent` used in the vela command):
   - **Local path:** `zz_vespa_smart_trap/cv_vespcv_grovevisionaiv2/himax/himax_vela.ini`
   - From repo root: `--config zz_vespa_smart_trap/cv_vespcv_grovevisionaiv2/himax/himax_vela.ini`  
   Alternatives: Seeed [vela_config.ini](https://files.seeedstudio.com/sscma/configs/vela_config.ini); or the snippet in [[himax vela]]; or config from [YOLOv8_on_WE2](https://github.com/HimaxWiseEyePlus/YOLOv8_on_WE2).

3. **Run Vela** (from repo root or use absolute paths for config and input):
   ```bash
   vela path/to/your_int8.tflite \
       --accelerator-config ethos-u55-64 \
       --config zz_vespa_smart_trap/cv_vespcv_grovevisionaiv2/himax/himax_vela.ini \
       --system-config My_Sys_Cfg \
       --memory-mode My_Mem_Mode_Parent \
       --output-dir output/
   ```
   The compiled model will be in `output/` (name often derived from the input, e.g. `your_int8_vela.tflite` or similar). Copy that file into `model_zoo/tflm_yolo11_od/` for flashing.

4. **If Vela fails** (e.g. unsupported ops or transpose): see [[himax vela]] (YOLO11n transpose issues, YOLOv8n as fallback). You may need an export that removes or replaces transpose ops (Himax YOLOv8_on_WE2 / YOLO11_on_WE2 flow).

**Action:** Reconstruct the pipeline: export .pt → int8 TFLite (Colab or local), then run Vela locally as above. Document the exact export and vela commands here once they work.

---

## 9. Troubleshooting (short)

- **Port in use:** `lsof | grep /dev/tty.usbmodem58FA1047631` then `kill -9 <PID>` if needed ([[himax gv2 troubleshooting]]).
- **Model won’t load:** Check size &lt;2.4 MB, format int8_vela.tflite, flash address 0xB7B000 ([[himax gv2 troubleshooting]]).
- **256×256 model:** A 256 model was tried and gave “no detection”; 224 worked ([[z_vespa_smart_trap/z model timeline 2025-07 - 2025-09]]). Prefer 192 or 224 for reliability.
- **Wrong flash address:** Using `0x3AB7B000` for the single YOLO11 OD model caused issues; use **0xB7B000** ([[himax cli flash model]]).

---

## 10. Source-of-truth references in this repo

| Topic              | Note |
|--------------------|------|
| Flash commands      | [[himax cli flash model]], [[himax cli flash yolo11n model]] |
| Build & image gen   | [[himax build firmware image]], [[gv2 build, copy, regenerate and flash]] |
| Environment & make  | [[himax environment]], [[himax makefile]], [[himax makefile met tflm_yolov8_od]] |
| GV2 constraints    | [[gv2 modelvoorwaarden]], [[himax gv2 troubleshooting]] |
| Vela & export issues| [[himax vela]], [[z_vespa_smart_trap/z yolo issue performance drop TFLite YOLOv8 YOLO11]] |
| Windows flash doc  | [[gv2 flash model windows version]] |
| Timeline Jul–Sep 25 | [[z_vespa_smart_trap/z model timeline 2025-07 - 2025-09]] |
| Working model name  | `yolo11n_2025-09-01_224_e300_full_integer_quant_vela.tflite` (see links above) |
| **Archive (model + GV2)** | See section 11 below |

---

## 11. Archive: model + GV2 notes (zzzArchive2025)

Notes recovered from git history (no longer in active vespa_smart_trap). All are in `zzzArchive2025/400 computer vision vespa gv2 models/`. Index:

- [[zzzArchive2025/400 computer vision vespa gv2 models/_index]] — index of archived notes
- [[yolov8n pt naar int8 vela tflite]] — export .pt → int8 TFLite + Vela command
- [[yolov8n imgsz 192 vs 640]] — comparison imgsz 640 vs 192 vs full integer quant TFLite
- [[pytorch naar full_integer_quantitized tflite]] — Colab paths, calibration, vela config, CAST warning

---

*Add the exact export and vela commands to section 8 once they work; this note then serves as the single guide for flashing a new YOLO11n model to GV2.*
