
**One-line purpose:** no longer in yolo
**Short summary:** 
**Agent:** archived

---

# YOLO QAT
- Niet standaard meer in YOLO [ref](https://github.com/ultralytics/ultralytics/issues/16688)
-  [QAT with YOLOv11](https://community.ultralytics.com/t/ultralytics-yolov11-qat/926)
- for Quantization-Aware Training (QAT) with Ultralytics YOLO11, we recommend using our built-in export functionality with `int8=True` argument rather than manual implementation.

# Export
model.export(format='tflite', int8=True, fraction=1.0, data='data.yaml')
