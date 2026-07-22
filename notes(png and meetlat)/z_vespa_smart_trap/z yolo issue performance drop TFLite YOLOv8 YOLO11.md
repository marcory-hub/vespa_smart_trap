

**One-line purpose:** yolov8 performance drop issue
**Short summary:** 
**Agent:** archived

---



Performancedrop bij quantificeeren van YOLOv8n zou aangepast moeten zijn door Ultralytics
- 
- YOLOv8 heeft veel meer performance drop dan YOLOv5 en YOLOx [ref](https://github.com/ultralytics/ultralytics/issues/9473)
- Veroorzaakt door de manier van exporteren
- At DeGirum, we have solved this problem and shared our [solution](https://github.com/ultralytics/ultralytics/issues/9473#issuecomment-2123437855) with the community. We maintain a fork of the ultralytics repo at [https://github.com/DeGirum/ultralytics_yolov8](https://github.com/DeGirum/ultralytics_yolov8).
- There is no need to retrain models on our fork. We only fix the export part of the code where we separate the post-processing (box decoding). This separation improves the accuracy quite a bit. We did submit a pull request that merges all our changes but it never got merged. This is the reason why we still maintain our repo.
- [Fix catastrophic accuracy degradation of TFLite static quantized integer models](https://github.com/ultralytics/ultralytics/pull/1695)
	- This PR fixes the problem that TFLite static quantized integer models detect nothing. (the problem was reported in [#1447](https://github.com/ultralytics/ultralytics/pull/1447) and in [#1683](https://github.com/ultralytics/ultralytics/issues/1683)).

YOLO11  hogere accuracy [ref](https://arxiv.org/html/2410.19869v2)
- **YOLO v8 (Nano):** 3.2 million parameters
- **YOLO v10 (Nano):** 2.3 million parameters
- **YOLO v11 (Nano):** 2.67 million parameters

