
**One-line purpose:** flash commands for the different models
**Short summary:** 
**Agent:** 
**Index:** [[himax from pt to flash]]

---
previous
1. [[himax installation on MacOS environment]]
2. [[himax makefile]] adjusted to tflm_yolov8_od or tflm_yolo11_od
3. [[himax build firmware]]
---


go to this directory
```sh
cd ~/Developer/vespa_smart_trap/himax/Seeed_Grove_Vision_AI_Module_V2
```

activate .venv
```sh
source .venv/bin/activate
```

Install prerequisites for xmodem
```sh
cd /Users/md/Developer/vespa_smart_trap/zz_vespa_smart_trap/cv_vespcv_grovevisionaiv2/himax/Seeed_Grove_Vision_AI_Module_V2
pip3 install -r xmodem/requirements.txt
```

connect gv2 with usb-c to mac

find COM port name with
```sh
ls /dev/tty.*
```
/dev/tty.usbmodem58FA1047631

```sh
sudo chmod 777 /dev/tty.usbmodem58FA1047631
```

Adjust 
- COM port
- file path
```sh
python3 xmodem/xmodem_send.py \
  --port=/dev/tty.usbmodem58FA1047631 \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=/Users/md/Developer/vespa_smart_trap/himax/Seeed_Grove_Vision_AI_Module_V2/we2_image_gen_local/output_case1_sec_wlcsp/output.img
```

```sh
python3 /Users/md/Developer/cv_vespcv_acc/Himax1/Seeed_Grove_Vision_AI_Module_V2/xmodem/xmodem_send.py \
  --port=/dev/tty.usbmodem58FA1047631 \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=/Users/md/Developer/cv_vespcv_acc/Himax1/Seeed_Grove_Vision_AI_Module_V2/we2_image_gen_local/output_case1_sec_wlcsp/output.img
```

if the example works continue with
1 [[himax flash command firmware]]
