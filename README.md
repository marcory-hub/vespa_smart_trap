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

## Example Command (adjustcu.usbmodem#####)

```bash
python xmodem/xmodem_send.py \
  --port=/dev/cu.usbmodem##### \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img \
  --model="model_zoo/tflm_yolo11_od/yolo11n_vespa_2026-02v1_allpxNULL_full_integer_quant_vela.tflite 0xB7B000 0x00000"
```

## Himax AI Web Toolkit

A visual tool showing live GV2 camera feed with real-time detection boxes.

- **Download:** `wget https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2/releases/download/v1.1/Himax_AI_web_toolkit.zip`
- **Extract:** `unzip Himax_AI_web_toolkit.zip`
- **Open:** Open `index.html` in browser (from the extracted folder)
- **Connect:** Select "Grove Vision" and click Connect 

# UART1 (GV2 TX-RX)

## firmware for GV2
  - kMinDetectionConfidence = 0.60f threshold (field test is needed to fine tune the threshold)
  - sends  I2C and UART: class 3 (vespa velutina) state 1, other classes state 2
  - kMinCaptureConfidence = 0.10f is use for the transmissing of the jpeg (to be finetuned when the camera is in the model)
  - I2C: adress 0x63, pins SCL and SDA
  - UART1
    - USE_DW_UART_1, 921600 baud
    - Pins: PB6 = UART1 RX, PB7 = UART1 TX (D6/D7 — cross to the ESP32 TX/RX)
    - sends: state (example: recv #242 len=5444 state=1 class=3 conf_u8=219 conf=0.859)(conf is redundant (=conf_u8/255)) and raw jpg bites (images not tested)
    - 
example flash command to flash the model trained on all images incl null images from gv2_firmware folder. Adjust `cu.usbmodem####`
```
python xmodem/xmodem_send.py --port=/dev/cu.usbmodem#### --baudrate=921600 --protocol=xmodem --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img --model="/Users/md/Developer/vespa_smart_trap/gv2_firmware/model_zoo/tflm_yolo11_od/yolo11n_vespa_2026-02v1_allpxNULL_full_integer_quant_vela.tflite 0xB7B000 0x00000"
```

## ESP32-S3
- gv2_uart_esp32_led is used to test gv2-uart firmware
- serial1 at 921600 baud, GPIO43/44 cross TX/RX with gv2
- receives 1-byte detection state  (0x00 / 0x01 vespa velutina / 0x02 other) and jpg
  - jpg used because a little smaller, faster and can be save and watched from SD. (no need for base64 because images are only for further training of the model)
- might be needed to use state to send jpg to SD (with gv2 unconnected I had some noise)
- flash command `gv2_uart_esp32_led` folder 
```
pio run
pio run -t upload
pio device monitor -b 115200
```

Run python3 `scripts/capture_gv2_uart_jpeg.py /dev/cu.usbmodem1101 921600` to save the next recv #... len=... JPEG from the ESP32 as frame_XXXX.jpg.