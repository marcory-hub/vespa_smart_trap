**One-line purpose:** use of grounding dino for zero knowledge prompt annotation 
**Short summary:** no longer used, replaced by earlier yolo models
**Agent:** archived

---

[[dataset zip command]]

[[vcv dataset annotatie instructie]]
1. **Dubbelen verwijderd met**: [findDuplicated.ipynb](https://github.com/vespCV/vespAgent/blob/main/datasetCurration/findDuplicates.ipynb)
2. [[grounding DINO py code]] : [Grounding DINO github](https://github.com/vespCV/vespAgent/blob/main/datasetCurration/GroundingDINOboundingBoxes.ipynb)
###### Archief
[[z data annotation with CVAT]]
## importeren in Roboflow
- correctie annotaties
- verdelen in 70-20-10
- exporteren als YOLOv8 en YOLO11
## hernoemen
- Hernoemd naar korte naam met [renameYoloJpgTxt.py](https://github.com/vespCV/vespAgent/blob/main/datasetCurration/renameYoloJpgTxt.py)
## optioneel: datasets van verschillende grootte maken
- [resizeDataset](https://github.com/vespCV/vespAgent/blob/main/datasetCurration/resizeDataset)
