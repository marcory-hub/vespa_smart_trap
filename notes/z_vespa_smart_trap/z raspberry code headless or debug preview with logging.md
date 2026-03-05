
**One-line purpose:** code for headless detector
**Short summary:** 
**Agent:** archived

---



```python
import time
import cv2
from datetime import datetime
from pathlib import Path
from core.detector import HornetDetector
from utils.logger import DetectionLogger

def main():
    detector = HornetDetector()
    logger = DetectionLogger(detector.config['logging']['log_file'])

    debug = detector.config.get("debug", {}).get("enabled", False)
    image_dir = Path(detector.config['logging']['image_output_dir'])
    image_dir.mkdir(parents=True, exist_ok=True)

    print("[INFO] Starting detection loop (15s interval)...")
    try:
        while True:
            frame = detector.picam2.capture_array()
            results = detector.detect(frame)
            annotated = detector.annotate_frame(frame, results)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            img_name = f"detection_{timestamp}.jpg"
            image_path = image_dir / img_name
            cv2.imwrite(str(image_path), annotated)

            num_detections = len(results[0].boxes)
            logger.log(str(image_path), num_detections)

            print(f"[LOG] {img_name} | Detections: {num_detections}")

            if debug:
                cv2.imshow("Debug Preview", annotated)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            time.sleep(15)

    except KeyboardInterrupt:
        print("\n[INFO] Exiting detection loop.")
        cv2.destroyAllWindows()

```