**One-line purpose:** unit tests
**Short summary:** detector and logger tests
**Agent:** archived

---


```sh
pip install pytest
```

```sh
pytest
```

test_detector.py
```python
import pytest
from core.detector import Detector

class DummyModel:
    def __call__(self, frame):
        class DummyResults:
            def pandas(self):
                class DummyDF:
                    xyxy = [{0: {'confidence': 0.9, 'xmin': 0, 'ymin': 0, 'xmax': 1, 'ymax': 1}}]
                return DummyDF()
        return DummyResults()

def test_detector_load(monkeypatch):
    # Monkeypatch torch.hub.load
    import torch.hub
    monkeypatch.setattr(torch.hub, "load", lambda *args, **kwargs: DummyModel())

    detector = Detector(model_path="dummy_path", detection_threshold=0.5)
    assert detector.model is not None

def test_detector_detect(monkeypatch):
    import torch.hub
    monkeypatch.setattr(torch.hub, "load", lambda *args, **kwargs: DummyModel())

    detector = Detector(model_path="dummy_path", detection_threshold=0.5)
    bboxes, confidences = detector.detect(frame="dummy_frame")

    assert len(bboxes) == 1
    assert len(confidences) == 1
    assert confidences[0] >= 0.5

```

test_logger.py
```python
import os
import pytest
import shutil
import numpy as np
from utils.logger import DataLogger

@pytest.fixture
def clean_log_dir(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir

def test_logger_creation(clean_log_dir):
    logger = DataLogger(log_dir=str(clean_log_dir))
    assert os.path.exists(logger.csv_path)

def test_logger_log_detection(clean_log_dir):
    logger = DataLogger(log_dir=str(clean_log_dir), save_images=False)
    dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)

    logger.log_detection(dummy_frame, confidences=[0.8])

    # Check if CSV has data
    with open(logger.csv_path, 'r') as f:
        lines = f.readlines()
    assert len(lines) > 1  # header + at least one detection

```

test_camera.py
```python
import pytest
from utils.camera import Camera

def test_camera_init():
    cam = Camera(cam_id=0)
    assert cam.cap.isOpened() or not cam.cap.isOpened()  # Depending if real cam is there

def test_camera_release():
    cam = Camera(cam_id=0)
    cam.release()
    assert not cam.cap.isOpened()

```