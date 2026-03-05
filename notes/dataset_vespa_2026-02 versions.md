**One-line purpose:** index of versions of the dataset 
**Short summary:** train 33020 images, 224 backgrounds, validation 5439 images and 224 backgrounds
**Agent:** 

---


v1 nopre-noaug
v2 192-noaug
v3 nopre-aug
v4 192-aug
v5 640x640
v6 320x320
v7 224x224
v8 192x192

Formats
Versions needed:
- train_valid_test_coco --> for swift-yolo training
- train_valid_test_yolo --> for ultralytics yolo training

Versions to keep on ssd:
- train_valid_test_coco --> for swift-yolo training
- train_valid_test_yolo --> for ultralytics yolo training
- coco_yolo per class (if needed for other models in the future)
- [[dataset cvat yolo format]] 
- merged yolo26 (if other train-valid-test are needed)


