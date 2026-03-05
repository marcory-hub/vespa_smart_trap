
**One-line purpose:** inference loop
**Short summary:** 
**Agent:** archived

---



```python
import time
from datetime import datetime
import os

def main():
    detector = HornetDetector()
    image_dir = Path(detector.config['logging']['image_output_dir'])
    image_dir.mkdir(parents=True, exist_ok=True)

    print("[INFO] Starting 15-second detection loop... Press Ctrl+C to exit.")

    try:
        while True:
            frame = detector.picam2.capture_array()
            results = detector.detect(frame)
            annotated = detector.annotate_frame(frame, results)

            # Save image with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = image_dir / f"detection_{timestamp}.jpg"
            cv2.imwrite(str(image_path), annotated)

            print(f"[LOG] Saved: {image_path}")
            time.sleep(15)  # Wait 15 seconds

    except KeyboardInterrupt:
        print("\n[INFO] Detection loop stopped.")

```