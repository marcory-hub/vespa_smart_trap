
**One-line purpose:** 
**Short summary:** 
**Agent:** 

---

**One-line purpose:** timeline of training yolov8n, yolo11n and swift-yolo
**Short summary:** yolov8n, yolo11n and swift-yolo trained with dataset hornet3000 and dataset_vespa_17000
**Agent:** archived

---

### ✅ Dataset Opschoning 
2025-07-01
- **vzon verwijderd**: Dataset opgeschoond van niet-relevante data
- **Test herverdeling**: Test data verdeeld over train (70%) en val (30%)
### ✅ Model Training Analyse
2025-07-03
- **YOLOv8n vs YOLO11n**: Vergelijking tussen modellen
- **Batch Size Analyse**: Optimalisatie van batch grootte
- **Learning Rate Analyse**: Optimalisatie van learning rate
- **Parameter Analyse**: Uitgebreide parameter optimalisatie
### ✅ Model Vergelijking en Optimalisatie
2025-07-05
- **Best Configuration (2025-07-05a)**:
  - mAP50-95: 0.856 (beste overall)
  - vvel mAP50-95: 0.873 (uitstekend - primair doel)
  - amel mAP50-95: 0.799 (secundair verbeteringsdoel)
  - Config: lr0=0.005, batch=128, cls=1.0, warmup=5.0

- **VVEL Performance Analyse**:
  - mAP50: 0.990 (uitstekende detectie rate)
  - Precision: 0.966 (hoge confidence voorspellingen)
  - Recall: 0.962 (goede dekking)
  - Sample Size: 708 instances (goede representatie)

### ✅ Image Size Optimalisatie -> 192
2025-07-13
- **Image Size 240**: Test met 240x240 resolutie (max voor Grove Vision AI V2)
- **Resultaat**: Niet optimaal voor YOLO (meeste voorbeelden zijn 192x192px)
- imgsz must be a multiple of 32 for YOLO
- **Image Size 192**:  (2^6)
### ✅ SenseCraft AI Platform - pretrained models
2025-07-18
- **Apple Detection Test**: Test van SenseCraft platform
- **Swift-YOLO**: geen andere yolo versies mogelijk
### ✅ Swift-YOLO Training
2025-07-19
[[swift-YOLO 2025-07-19]]
- Labelling Datasets in Roboflow [[accm vespCV dataset Roboflow]]
- Training Dataset Exported Model in Google colab
	1. [Colab Digital Meter Water Swift-YOLO_192](https://colab.research.google.com/github/seeed-studio/sscma-model-zoo/blob/main/notebooks/en/Digital_Meter_Water_Swift-YOLO_192.ipynb) aangepast voor eigen dataset en 
	2. ✅ Colab [Vespa velutina Detection - Swift-YOLO_192](https://colab.research.google.com/drive/1e_ravYhrvqVZajYGZKQ5r-B3a0fvfI4p) 2025-07-18
	3. Resultaat: - /Users/md/Developer/vespCVacc/accModels/swiftYolo_25-07-19_192/Digital_Meter_Water_Swift-YOLO_192/epoch_100_int8_vela.tflite
- Swift-yolo model werkt, maar accuracy is veel te laag
- **Probleem**: Swift-YOLO performance te laag voor praktische toepassing (gebaseerd op yolov5, dus ongeschikt voor kleine objecten)

### ❌ Edge Impuls
2025-08-16
- Dit platform getest om te flashen
	1. [[z edge impulse CLI Installation]]
	2. [[z edge impulse Himax flash tool]]
- Problemen
	- **Missing `./flash_mac.command`**: This file doesn't exist in the current Edge Impulse firmware package (opgelost via .py in folder xmodem)
	- **Bootloader corruption**: After Edge Impulse firmware flash, bootloader became unresponsive
- Ook getest op raspberry pi met bookworm.
### ✅ Flash bestaande yolov8 model
2025-08-23
- [[himax environment]]
- [[himax build firmware image]]
- [[himax flash firmware first time]]
- [[himax makefile met tflm_yolov8_od]]
- [[himax ai web toolkit installation]]
### ✅ Preformance drop door imgsz
2025-08-24
- [[z yolo qat quantization aware training]] dit word reeds gedaan door ultralytics export 
- [[z yolo issue performance drop TFLite YOLOv8 YOLO11]]
- Verschil tussen [[yolov8n comparison imgsz 192 vs 640]]  vooral door imgsz van 640 naar 192
### ✅ Flash modelzoo modellen
2025-08-25
- yolov8_pose
- yolo11_192
- yolo11_224
- [[acc netron vergelijking modellen seeed vs custom]]
- [[himax modellen uit modelzoo flashen]]
### ❌ conversion pt to onnx to TFLite to vela
2025-08-30
- yolov8n coco 80cls en vespCV
### ❌Open YOLO11_on_WE2_Tutorial.ipynb on Colab
2025-08-30
- [[colab yolo open YOLO11_on_WE2_Tutorial.ipynb on Colab]] module imp ontbreekt sinds python 3.12, bugfix niet gevonden
### ✅ YOLO11 on WE2
- [[acc yolo11 on we2 for PC on Colab]]
### ✅ YOLO11 imgsz224 optimalisatie
2025-09-02
- [[yolo11n_25-09-01a_224_e300]] blijft de beste
### ❌Test met grotere afmetingen
- test of webtool ook hardcoded imgsz heeft
- test met 
#### 256 5.4 MB -> geen detectie
```
Failed to resize buffer. Requested: 573696, available 443064, missing: 130632
```

#### 224px model log

Model loads successfully.
Interpreter prints tensor shapes:

input  [1, 224, 224, 3]  (150,528 bytes INT8)
output0 [1, 28, 28, 68]
output1 [1, 7, 7, 68]
output2 [1, 14, 14, 68]

yolo11 object detect invoke pass

Inference runs successfully.

Only warning is:

buffer_size: 2505 may be too small reallocating
if still fail, please modify linker script heap size

→ Not fatal, just a reallocation fallback.

---






