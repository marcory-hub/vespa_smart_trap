**One-line purpose:** index for himax sdk
**Short summary:** documentation, cli commands to build and flash the model
**SoT:**
**Agent:** when flashing gv2 with himax is considered, users should update this index and linked files
**Main Index:** [[__vespa_smart_trap]]

---
# quick links
- [[himax build firmware image]]
- [[himax flash command firmware]]

---
# Overview
```
YOLO (PyTorch)
   ↓
INT8 TFLite (Ultralytics export)
   ↓
Vela compiler
   ↓
int8_vela.tflite (NPU optimized)
   ↓
copy int8_vela.tflite to modelzoo
   ↓
adjust path in flash command to modelzoo/int8_vela.tflite 
   ↓
flash model
```

---

# 1. train, quantize and compile model
1. Train yolo model
	1. [YOLO11n Training on Google Colab](https://github.com/marcory-hub/yolo11n-on-grove-vision-ai-v2#:~:text=1.-,YOLO11n%20Training%20on%20Google%20Colab,-A%20notebook%20to) 2026-02-19
2. Full integer quantization and vela conversion
	1. [YOLO11n Full Integer Quantization and VELA Conversion for Grove Vision AI V2](https://github.com/marcory-hub/yolo11n-on-grove-vision-ai-v2#:~:text=2.-,YOLO11n%20Full%20Integer%20Quantization%20and%20VELA%20Conversion%20for%20Grove%20Vision%20AI%20V2,-This%20notebook%20handles) 2026-02-25
3. [[gv2 model requirements]]
- latest yolo11n models for deployment on gv2
- made with dataset 2026-02v1 (no preprocessing, no augmentation)
- 30-40-60px object size [[dataset pixelsize raspberry cam 1.3 at 10 cm]]
## 2. full integer quantization and vela conversion
- github [yolo11n-on-grove-vision-ai-v2](https://github.com/marcory-hub/yolo11n-on-grove-vision-ai-v2)
- colab [yolo11n training](https://colab.research.google.com/drive/1TGsNgTjzIeN_jRtQZf-Y3opKIXQ82djo?usp=sharing)
- colab [yolo pt to vela](https://colab.research.google.com/drive/1TGsNgTjzIeN_jRtQZf-Y3opKIXQ82djo?usp=sharing)
- [[vela]] background information, a tool to compile a for TensorFlow Lite  (.tflite) for Microcontrolers
## 3. Himax installation
- [[himax installation on MacOS environment]]
- [[himax build firmware first install]]
## 4. Himax build firmware image
- [[himax makefile]] **APP_TYPE** tflm_yolo11_od  
- [[himax install xmodem]]
- [[himax restore gv2 factory settings]]
- [[himax coco_classes fix]]
## 5. Himax update and firmware image
- [[himax flash command firmware]]
# 6. Himax AI web toolkit
- [[himax ai web toolkit installation]]
- [[himax terminal gv2 output]]
# Troubleshooting
- [[himax gv2 troubleshooting]]


---





- [[gv2 build, copy, regenerate and flash]], connect gv2 via usb-c, check flash without model, flash model
- [[himax environment]], python, pip, make, arm gnu toolchain for mac silicon, gccv check
- [[himax ai web toolkit installation]]
- [[himax makefile]]
- [[himax makefile met tflm_yolov8_od]]

- [[himax flash firmware first time]]
- [[himax modelzoo readme]]
- [[himax modellen uit modelzoo flashen]]
- [[himax cli flash model]], flash commands for the different models (and results)








**[[z himax_yolo26]]**
2026-03-10
- deployment failed
- issues 
	- multiple object bounding boxes for one object
	- incorrect location of obb's
- zzz_archive/himax_yolo26_attempt_2026-03-10.zip

