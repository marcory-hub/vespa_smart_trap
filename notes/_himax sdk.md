**One-line purpose:** index for himax sdk
**Short summary:** documentation, cli commands to build and flash the model
**Agent:** when flashing gv2 with himax is considered, users should update this index and linked files
**Main Index:** [[__vespa_smart_trap]]

---
# quick links
- [[_model]] train, quantize, compile model, model index
- [[himax build firmware image]]
- [[himax flash command firmware]]

---
# overview
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
## himax installation
- [[himax installation on MacOS environment]]
- [[himax build firmware first install]]
- [[himax install xmodem]]
## himax build firmware image
- [[himax makefile]] **APP_TYPE** tflm_yolo11_od  
- [[himax restore gv2 factory settings]]
- [[himax coco_classes fix]]
## himax update and firmware image
- [[himax flash command firmware]]
# himax AI web toolkit
- [[himax ai web toolkit installation]]
- [[himax terminal gv2 output]]
# troubleshooting
- [[himax gv2 troubleshooting]]
- [[himax find flash address]]

---
# archief

**[[z himax_yolo26]]**
- https://www.ultralytics.com/glossary/intersection-over-union-iou
- https://www.reddit.com/r/Ultralytics/comments/1r401zg/yolo26_double_detection/
- export tflite with nms=true (default = false) not possible with int8
- end2end=None --> not a valid yolo argument
2026-03-10
- deployment failed
- issues 
	- multiple object bounding boxes for one object
	- incorrect location of obb's
- zzz_archive/himax_yolo26_attempt_2026-03-10.zip

