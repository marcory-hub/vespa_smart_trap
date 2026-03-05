**One-line purpose:** code to run inference with camera on raspberry pi
**Short summary:** 
**Agent:** archived

---

https://docs.ultralytics.com/guides/raspberry-pi/#inference-with-camera
```python
import cv2
from picamera2 import Picamera2

from ultralytics import YOLO

# Initialize the Picamera2
picam2 = Picamera2()
picam2.preview_configuration.main.size = (1280, 720)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

# Load the YOLO11 model
model = YOLO("yolo11n.pt")

while True:
    # Capture frame-by-frame
    frame = picam2.capture_array()

    # Run YOLO11 inference on the frame
    results = model(frame)

    # Visualize the results on the frame
    annotated_frame = results[0].plot()

    # Display the resulting frame
    cv2.imshow("Camera", annotated_frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) == ord("q"):
        break

# Release resources and close windows
cv2.destroyAllWindows()
```

chatgpt
```python
import cv2
from picamera2 import Picamera2
from ultralytics import YOLO
import yaml
from pathlib import Path

class HornetDetector:
    def __init__(self, config_path="config/config.yaml"):
        self.load_config(config_path)
        self.model = YOLO(self.config['model']['path'])
        self.setup_camera()

    def load_config(self, path):
        with open(path, "r") as file:
            self.config = yaml.safe_load(file)

    def setup_camera(self):
        self.picam2 = Picamera2()
        self.picam2.preview_configuration.main.size = tuple(self.config['camera']['resolution'])
        self.picam2.preview_configuration.main.format = "RGB888"
        self.picam2.preview_configuration.align()
        self.picam2.configure("preview")
        self.picam2.start()

    def detect(self, frame):
        results = self.model(frame)
        return results

    def annotate_frame(self, frame, results):
        return results[0].plot()

def main():
    detector = HornetDetector()
    while True:
        frame = detector.picam2.capture_array()
        results = detector.detect(frame)
        annotated = detector.annotate_frame(frame, results)
        cv2.imshow("Hornet Detector", annotated)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
```