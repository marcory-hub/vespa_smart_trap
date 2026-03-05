**One-line purpose:** index of all model files
**Key info:** training configs of yolov8s, yolov10, yolo11n and swift-yolo models
**Agent:** current swift-yolo model should trained with dataset_2026-2 (4 versions) and put on sensecraft.ai
**Main Index:** [[__vespa_smart_trap]]


---

# Current models
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
- [[yolo26n_vespa_2026-02v1_allpx_imgsz192]] no difference on sensecraft.ai between imgsz192 and imgsz224. Seems like 224px are reduced to 192. This is not the case when flashed with himax

- [[yolo26n_vespa_2026-02v1_60px_imgsz224]]
- [[yolo26n_vespa_2026-02v1_40px_imgsz224]]
- [[yolo26n_vespa_2026-02v1_30px_imgsz224]]

# Models for test purposes
- [[swiftyolo_epoch_100_int8_vela.tflite]] 

---

- [[_datasets]], workflow, vesp_2026-02, annotation, species, roboflow

- [[_colab]], swift-yolo training

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

