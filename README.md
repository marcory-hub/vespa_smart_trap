# GV2 YOLO11 Model Flashing Instructions

Quick reference to flash YOLO11 models to Grove Vision AI V2 on macOS.

## Setup (First Time Only)

- **Clone repo with submodules (all-in-one):** `git clone --recurse-submodules https://github.com/marcory-hub/vespa_smart_trap && cd vespa_smart_trap`
- **Or separately:** Clone first, then init: `git clone https://github.com/marcory-hub/vespa_smart_trap && cd vespa_smart_trap && git submodule update --init --recursive`
- **Create venv:** `python3 -m venv .venv && source .venv/bin/activate`
- **Install deps:** `pip install pyserial`

## Available Models

- `yolo11n_vespa_2026-02v1_30pxNULL_full_integer_quant_vela.tflite`
- `yolo11n_vespa_2026-02v1_40pxNULL_full_integer_quant_vela.tflite`
- `yolo11n_vespa_2026-02v1_60pxNULL_full_integer_quant_vela.tflite`
- `yolo11n_vespa_2026-02v1_allpxNULL_full_integer_quant_vela.tflite`

All located in: `gv2_firmware/model_zoo/tflm_yolo11_od/`

## Prerequisites

- USB-C cable connected to GV2 board
- Python 3.11+ with virtual environment activated: `source .venv/bin/activate`
- GV2 firmware already built (if not: `cd gv2_firmware/EPII_CM55M_APP_S && make APP_TYPE=tflm_yolo11_od`)

## Flashing Steps

1. **Identify USB port:** `ls /dev/cu.usbmodem*` (e.g., `/dev/cu.usbmodem58FA1047631`)
2. **Navigate to gv2_firmware:** `cd gv2_firmware`
3. **Run xmodem flash command:**
   ```bash
   python xmodem/xmodem_send.py \
     --port=PORT \
     --baudrate=921600 \
     --protocol=xmodem \
     --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img \
     --model="model_zoo/tflm_yolo11_od/MODEL_NAME.tflite 0xB7B000 0x00000"
   ```
   Replace `PORT` and `MODEL_NAME.tflite` accordingly.
4. **When prompted on GV2:** Press reset button; X-Modem will begin automatically
5. **Wait for completion:** Progress bar shows 100%, board reboots

## Example Command

```bash
python xmodem/xmodem_send.py \
  --port=/dev/cu.usbmodem58FA1047631 \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img \
  --model="model_zoo/tflm_yolo11_od/yolo11n_vespa_2026-02v1_allpxNULL_full_integer_quant_vela.tflite 0xB7B000 0x00000"
```

## Himax AI Web Toolkit

GUI tool for model deployment and board management.

- **Download:** `wget https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2/releases/download/v1.1/Himax_AI_web_toolkit.zip`
- **Extract:** `unzip Himax_AI_web_toolkit.zip`
- **Open:** Open `index.html` in browser (from the extracted folder)
- **Connect:** Select "Grove Vision" and click Connect to see xamera image with inference results
