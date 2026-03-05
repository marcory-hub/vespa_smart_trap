
**One-line purpose:** code for logger
**Short summary:** 
**Agent:** archived

---

```python
import csv
from pathlib import Path
from datetime import datetime

class DetectionLogger:
    def __init__(self, log_path="data/logs/detections.csv"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            with open(self.log_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "num_detections", "image_path"])

    def log(self, image_path, num_detections):
        timestamp = datetime.now().isoformat()
        with open(self.log_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, num_detections, image_path])

```