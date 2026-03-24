**One-line purpose:** flash command; modify with path to .tflite 
**Short summary:** flash command, SoT
**SoT:** yes
**Agent:** information about the flash command
**Index:** [[_himax sdk]]
Previous: [[himax build firmware image]]
Next: [[himax ai web toolkit installation]], [[himax gv2 troubleshooting]]

---
# flash command
```sh
python xmodem/xmodem_send.py --port=/dev/cu.usbmodem58FA1047631 --baudrate=921600 --protocol=xmodem --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img --model="/Users/md/Developer/vespa_smart_trap/gv2_firmware/model_zoo/tflm_yolo11_od/yolo11n_vespa_2026-02_imgsz224_full_integer_quant_vela_nopost.tflite 0xB7B000 0x00000"
```
- no such file? then cd ..
 - xmodem is located in /Users/md/Developer/vespa_smart_trap/himax/Seeed_Grove_Vision_AI_Module_V2
 - cu vs tty
 - 0x3AB7B000 0x00000

---
# Flash without model
```sh
   python3 xmodem/xmodem_send.py \
     --port=/dev/cu.usbmodem58FA1047631 \
     --baudrate=921600 \
     --protocol=xmodem \
     --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img
```

---
**SoT**
- baudrate: 921600
- check if COM port is correct `ls /dev/tty.*`
- nopost vela models are needed
- check makefile for APP_TYPE [[himax makefile]]
- usb-c is connected with data-cable, port is working (agent is not allow to check that, it is checked)

---
# requirements
## xmodem

```sh
cd /Users/md/Developer/vespCVacc/Himax/Seeed_Grove_Vision_AI_Module_V2
pip install -r xmodem/requirements.txt
```
use pip in .venv

---
# find port
```sh
ls /dev/tty.*
```

/dev/tty.usbmodem58FA1047631

```sh
sudo chmod 777 /dev/tty.usbmodem58FA1047631
```

---

# pose
adjust APP_TYPE to pose

```sh
python xmodem/xmodem_send.py \
  --port=/dev/tty.usbmodem58FA1047631 \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img \
  --model="model_zoo/tflm_yolov8_pose/yolov8n_pose_256_vela_3_9_0x3BB000.tflite 0x3BB000 0x00000"
```

---

