# GV2 YOLO11 Model Flashing Instructions

Quick reference to flash YOLO11 models to Grove Vision AI V2 on macOS.

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

1. **Identify USB port:**
   ```bash
   ls /dev/cu.usbmodem*
   ```
   (Replace `PORT` below with your identified port, e.g., `/dev/cu.usbmodem58FA1047631`)

2. **Navigate to gv2_firmware:**
   ```bash
   cd gv2_firmware
   ```

3. **Run xmodem flash command:**
   ```bash
   python xmodem/xmodem_send.py \
     --port=PORT \
     --baudrate=921600 \
     --protocol=xmodem \
     --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img \
     --model="model_zoo/tflm_yolo11_od/MODEL_NAME.tflite 0xB7B000 0x00000"
   ```
   Replace `MODEL_NAME.tflite` with one of the models listed above.

4. **Wait for completion:**
   - Progress bar will show 100% when done
   - Board will reboot automatically

## Example Command

```bash
python xmodem/xmodem_send.py \
  --port=/dev/cu.usbmodem58FA1047631 \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img \
  --model="model_zoo/tflm_yolo11_od/yolo11n_vespa_2026-02v1_allpxNULL_full_integer_quant_vela.tflite 0xB7B000 0x00000"
```

