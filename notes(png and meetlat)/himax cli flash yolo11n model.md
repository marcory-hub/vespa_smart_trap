
**One-line purpose:** flash command
**Short summary:** flash yolo11n to gv2
**Agent:** inactive

---

cd to Seeed folder
source .venv/bin
```sh
python3 xmodem/xmodem_send.py \
  --port=/dev/tty.usbmodem58FA1047631 \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img \
  --model="model_zoo/tflm_yolo11_od/yolo11n_2025-09-01_224_e300_full_integer_quant_vela.tflite 0xB7B000 0x00000"
```

