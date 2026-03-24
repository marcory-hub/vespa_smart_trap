**One-line purpose:** model training, quantization and compiling and an index of all model files
**Key info:** training configs of yolov8s, yolov10, yolo11n and swift-yolo models
**Agent:** current swift-yolo model should trained with dataset_2026-2 (4 versions) and put on sensecraft.ai
**Main Index:** [[__vespa_smart_trap]]

---
# train, quantize and compile model
1. Train yolo model
	1. [YOLO11n Training on Google Colab](https://github.com/marcory-hub/yolo11n-on-grove-vision-ai-v2#:~:text=1.-,YOLO11n%20Training%20on%20Google%20Colab,-A%20notebook%20to) 2026-02-19
2. Full integer quantization and vela conversion
	1. [YOLO11n Full Integer Quantization and VELA Conversion for Grove Vision AI V2](https://github.com/marcory-hub/yolo11n-on-grove-vision-ai-v2#:~:text=2.-,YOLO11n%20Full%20Integer%20Quantization%20and%20VELA%20Conversion%20for%20Grove%20Vision%20AI%20V2,-This%20notebook%20handles) 2026-02-25
3. [[gv2 model requirements]]
- latest yolo11n models for deployment on gv2
- made with dataset 2026-02v1 (no preprocessing, no augmentation)
- 30-40-60px object size [[dataset pixelsize raspberry cam 1.3 at 10 cm]]
## full integer quantization and vela conversion
- github [yolo11n-on-grove-vision-ai-v2](https://github.com/marcory-hub/yolo11n-on-grove-vision-ai-v2)
- colab [yolo11n training](https://colab.research.google.com/drive/1TGsNgTjzIeN_jRtQZf-Y3opKIXQ82djo?usp=sharing)
- colab [yolo pt to vela](https://colab.research.google.com/drive/1TGsNgTjzIeN_jRtQZf-Y3opKIXQ82djo?usp=sharing)
- [[vela]] background information, a tool to compile a for TensorFlow Lite  (.tflite) for Microcontrolers

---
# Current models
#### Models with NULL images
(Quantized and compiled 2026-03-24)
- yolo11n_vespa_2026v1_allpx_imgsz224
- yolo11n_vespa_2026v1_30px_imgsz224
- yolo11n_vespa_2026v1_40px_imgsz224
- yolo11n_vespa_2026v1_60px_imgsz224

#### Models without NULL images
[wandb vespa 2026-02](https://wandb.ai/mvdijk-vespcv/vespa_2026-02?nw=nwusermvdijk)
- [[yolo11n_vespa_2026-02v1_imgsz224]] slightly better than yolo26n
	- mAP50           | 0.9779  | 0.9731  | -0.0047
	- mAP50-95 (mean) | 0.8064  | 0.7736  | -0.0328
	- vcra 0.8345
	- vvel 0.7862
- [[yolo26n_vespa_2026-02v1_allpx_imgsz224]] 
	- mAP50-95
	- vcra 0.747035
	- vvel 0.769797


# Models for test purposes
- [[swiftyolo_epoch_100_int8_vela.tflite]] 

---

- [[_datasets_vst]], workflow, vesp_2026-02, annotation, species, roboflow

- [[_colab to do aanvullen]], swift-yolo training

- [[ultralytics yolo documentation]] 
- [[swift-yolo documentation]]
- [[swift-yolo 192 Roboflow-Colab-SenseCraft]]

- [[yolo11 license citations and acknowledgment]]
- [[yolo config.yaml]]


**Best models**
espet_pico_vespcv_acc2025-12
yolo11n_2025-09-01-224_e300
yolo11n_2025-09-01-224_e300
swiftYolo_2025-07-19_imgsz192
yolo11n_2025-07-10a_imgsz192
yolo11n_2025-07-14a_imgsz192
yolo11n_2025-07-15_192_full_int8.tflite
yolo11n_2025-04-17000

# Archive
- [[z yolo issue performance drop TFLite YOLOv8 YOLO11]]
- [[z model timeline 2025-07 - 2025-09]]
- [[z models online]]
- [[z yolo qat quantization aware training]]

[[yolov8n_analysis]]
[[yolo11n and 8n parameter analysis]]
[[yolo11n and 8n  model comparison]]
[[yolo11n 8n batch size analysis]]


**Archived models zipped**
/Users/md/Developer/cv_vesp_modellen/zzArchief
vespcvSwiftYolo20250715_epoch100
vespCVyolo11n20250421_default
vespCVyolo11n20250705a[[yolo11n_2025-07-05a_b128]]
vespCVyolo11n20250705b[[yolo11n_2025-07-05b]]
vespCVyolo11n20250705c[[yolo11n_2025-07-05c]]
vespCVyolo11n20250706a
[[vespCVyolo11n20250810a]]
vespCVyolo8n20250703
vespCVyolo8n20250704a
vespCVyolo8n20250704b
vespCVyolo8n20250704c
vespCVyolo8n20250705a
vespCVyolo8n20250713a
vespCVyolo8n20250714a
[[yolo11n_25-09-01a_224_e300]]
yolo11n_25-09-21_224_e300_b512
yolo11n_2025-08-31a_224_e10
[[yolo11n_2025-09-01_224_e300]]
[[yolo11 2025-09-01 colab notebook notes]]
[[yolo11n_25-09-01a_224_e300_colab]]
[[yolo11n_2025-09-02_224_e300_b512]]
yolo11n_imgsz256-384_e10

