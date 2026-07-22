**One-line purpose:** code to log data
**Short summary:** logs detections, temperature, time
**Agent:** archived

---

utils/logger.py
```python
import os
import csv
from datetime import datetime
import cv2

class DataLogger:
    def __init__(self, log_dir="data/logs/", save_images=True, confidence_threshold=0.7):
        self.log_dir = log_dir
        self.save_images = save_images
        self.confidence_threshold = confidence_threshold

        os.makedirs(self.log_dir, exist_ok=True)
        self.csv_path = os.path.join(self.log_dir, "detections.csv")

        # Create CSV file with header if not exist
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "confidence", "image_filename"])

    def log_detection(self, frame, confidences):
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H_

```

```python
import psutil

cpu_temp = psutil.sensors_temperatures()['cpu-thermal'][0].current
cpu_percent = psutil.cpu_percent()

```

```sh
psutil
```

```python
pip install psutil
```

```python
import os
import csv
import cv2
import psutil
from datetime import datetime

class DataLogger:
    def __init__(self, log_dir="data/logs/", save_images=True, confidence_threshold=0.7):
        self.log_dir = log_dir
        self.save_images = save_images
        self.confidence_threshold = confidence_threshold

        os.makedirs(self.log_dir, exist_ok=True)
        self.csv_path = os.path.join(self.log_dir, "detections.csv")

        # Create CSV file with extended header
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "confidence", "image_filename", "cpu_temp_c", "cpu_usage_percent"])

    def get_system_stats(self):
        try:
            temps = psutil.sensors_temperatures()
            if 'cpu-thermal' in temps:
                cpu_temp = temps['cpu-thermal'][0].current
            else:
                cpu_temp = None
        except Exception:
            cpu_temp = None

        cpu_usage = psutil.cpu_percent(interval=1)  # measure over 1 second
        return cpu_temp, cpu_usage

    def log_detection(self, frame, confidences):
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

        cpu_temp, cpu_usage = self.get_system_stats()

        if not confidences:
            return  # Nothing to log

        for confidence in confidences:
            if confidence >= self.confidence_threshold:
                image_filename = f"{timestamp}_{int(confidence*100)}.jpg" if self.save_images else ""
                if self.save_images:
                    image_path = os.path.join(self.log_dir, image_filename)
                    cv2.imwrite(image_path, frame)

                with open(self.csv_path, mode='a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        timestamp,
                        f"{confidence:.2f}",
                        image_filename,
                        f"{cpu_temp:.2f}" if cpu_temp is not None else "N/A",
                        f"{cpu_usage:.2f}"
                    ])

```