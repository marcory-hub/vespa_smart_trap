**One-line purpose:** code to run detection on raspberry
**Short summary:** load model, get image every 15s, run detection
**Agent:** archived

---
1. laad model
2. verkrijg camera input iedere 15 sec
3. run detection 


```python
class Detector:
    def __init__(self, model_path: str, threshold: float):
        self.model_path = model_path
        self.threshold = threshold
        self.model = self.load_model()

    def load_model(self):
        # placeholder, later you load YOLO
        return None

    def detect(self, frame):
        # placeholder
        return [], []

```

verbeterde startversie
```python
import torch
import time

class Detector:
    def __init__(self, model_path: str, detection_threshold: float):
        self.model_path = model_path
        self.threshold = detection_threshold
        self.model = self.load_model()

    def load_model(self):
        print(f"[INFO] Loading model from {self.model_path}")
        model = torch.hub.load('ultralytics/yolo10', 'custom', path=self.model_path, force_reload=True)
        return model

    def detect(self, frame):
        results = self.model(frame)
        detections = results.pandas().xyxy[0]

        bboxes = []
        confidences = []

        for _, row in detections.iterrows():
            if row['confidence'] >= self.threshold:
                bboxes.append((row['xmin'], row['ymin'], row['xmax'], row['ymax']))
                confidences.append(row['confidence'])

        return bboxes, confidences

```

run.py
```python
import time
import yaml
from core.detector import Detector
from utils.camera import Camera

def load_config(path="config/base_config.yaml"):
    with open(path, 'r') as file:
        return yaml.safe_load(file)

def main():
    config = load_config()

    detector = Detector(
        model_path=config['model']['path'],
        detection_threshold=config['model']['detection_threshold']
    )
    camera = Camera(
        cam_id=config['camera']['id'],
        width=config['camera']['width'],
        height=config['camera']['height'],
        fps=config['camera']['fps']
    )

    print("[INFO] Starting detection loop...")

    try:
        while True:
            frame = camera.read_frame()
            if frame is None:
                print("[ERROR] Failed to read frame.")
                continue

            bboxes, confidences = detector.detect(frame)
            print(f"[DETECTION] Found {len(bboxes)} objects.")

            # OPTIONAL: Save frame or do something else

            time.sleep(15)  # wait for 15 seconds
    except KeyboardInterrupt:
        print("\n[INFO] Exiting...")
    finally:
        camera.release()

if __name__ == "__main__":
    main()

```

