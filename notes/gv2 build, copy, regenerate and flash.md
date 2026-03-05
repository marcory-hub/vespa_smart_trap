
**One-line purpose:** use himax sdk to flash the model
**Short summary:** connect gv2 via usb-c, check flash without model, flash model
**Agent:** current stack, himax sdk

---


Verbindt gv2 met usb-c
CD naar S
```sh
cd Himax_gv2_esp32/Seeed_Grove_Vision_AI_Module_V2/
source .venv/bin/activate
```

```bash
# From Seeed.... 
cd "EPII_CM55M_APP_S"

make clean && make

cp obj_epii_evb_icv30_bdv10/gnu_epii_evb_WLCSP65/EPII_CM55M_gnu_epii_evb_WLCSP65_s.elf ../we2_image_gen_local/input_case1_secboot/EPII_CM55M_gnu_epii_evb_WLCSP65_s.elf
   
cd ../we2_image_gen_local
./we2_local_image_gen_macOS_arm64 project_case1_blp_wlcsp.json

cd ..
```

flash zonder model
```sh
   python3 xmodem/xmodem_send.py \
     --port=/dev/cu.usbmodem58FA1047631 \
     --baudrate=921600 \
     --protocol=xmodem \
     --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img
```

check of 
```
python3 xmodem/xmodem_send.py \
  --port=/dev/cu.usbmodem58FA1047631 \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img \
  --model="model_zoo/tflm_yolo11_od/yolo11n_2025-09-01_224_e300_full_integer_quant_vela.tflite 0xB7B000 0x00000"
```

let op --port=/dev/cu.usbmodem58FA1047631 \ ipv not /dev/tty.usbmodem* on macOS.

output 
```
screen /dev/cu.usbmodem58FA1047631
```

```
screen /dev/cu.usbmodem101
```

