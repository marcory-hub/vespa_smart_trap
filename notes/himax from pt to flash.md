
**One-line purpose:** *index* for himax sdk
**Short summary:** quick reference, documentation, cli commands to build and flash the model
**Agent:** when flashing gv2 with himax is considered. Go to [[_grove vision ai v2]] for hardware documentation of the gv2.
**Main Index:** [[__vespa_smart_trap]]

---

# Quick link
- [[himax flash command firmware]] to flash new model 

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

# 1. yolov8n and yolo11n for object detection
1. Train yolo model [YOLO11n Training on Google Colab](https://github.com/marcory-hub/yolo11n-on-grove-vision-ai-v2#:~:text=1.-,YOLO11n%20Training%20on%20Google%20Colab,-A%20notebook%20to) 2026-02-19
2. Full integer quantization and vela conversion [YOLO11n Full Integer Quantization and VELA Conversion for Grove Vision AI V2](https://github.com/marcory-hub/yolo11n-on-grove-vision-ai-v2#:~:text=2.-,YOLO11n%20Full%20Integer%20Quantization%20and%20VELA%20Conversion%20for%20Grove%20Vision%20AI%20V2,-This%20notebook%20handles) 2026-02-25

[[gv2 model requirements]]
latest yolo11n models for deployment on gv2
- made with dataset 2026-02v1 (no preprocessing, no augmentation)
- 30-40-60px object size [[dataset pixelsize raspberry cam 1.3 at 10 cm]]
## 2. full integer quantization and vela conversion
- github [yolo11n-on-grove-vision-ai-v2](https://github.com/marcory-hub/yolo11n-on-grove-vision-ai-v2)
- colab [yolo11n training](https://colab.research.google.com/drive/1TGsNgTjzIeN_jRtQZf-Y3opKIXQ82djo?usp=sharing)
- colab [yolo pt to vela](https://colab.research.google.com/drive/1TGsNgTjzIeN_jRtQZf-Y3opKIXQ82djo?usp=sharing)
- [[vela]] background information, a tool to compile a for TensorFlow Lite  (.tflite) for Microcontrolers
## 3. Himax installation
- [[himax installation on MacOS environment]]
## 4. Himax build firmware image
- check [[himax makefile]] how to change **APP_TYPE** to tflm_yolov8_od or tflm_yolo11_od 
- [[himax build firmware]]
- [[himax install xmodem]]
- [[himax cli flash yolov8n_pose]] flash command
- [[himax cli flash 2025 yolo11n model]] flash command
- [[himax how to restore to the original factory settings]], himax or sensecraft restore
- [[himax coco_classes fix]], path to file with the hardcoded COCO classes array
## 5. Himax update and firmware image
- [[himax flash command firmware]]

# Troubleshooting
- [[himax gv2 troubleshooting]]














