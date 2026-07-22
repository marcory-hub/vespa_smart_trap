**One-line purpose:** code to focus, calibrate
**Short summary:** 
**Agent:** archived

---


```python
import cv2

class Camera:
    def __init__(self, cam_id=0, width=640, height=480, fps=30):
        self.cap = cv2.VideoCapture(cam_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)

    def read_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        self.cap.release()

```



| Feature                | libcamera                | Picamera2                      |
| ---------------------- | ------------------------ | ------------------------------ |
| Level                  | Low-level (C++/bindings) | High-level (Python)            |
| Interface              | CLI, C++ API             | Python API                     |
| Autofocus control      | ✔️ Full control          | ✔️ Via `set_controls()`        |
| Good for Raspberry Pi? | ✔️ Core library          | ✔️ Best choice for Python devs |
| Lens manual focus?     | ✔️                       | ✔️ Yes (`AfModeEnum.Manual`)   |


manual focus with picamera2

chatgpt
```python
from picamera2 import Picamera2, Preview
from libcamera import controls

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())

# Set manual focus (disable AF)
picam2.set_controls({
    "AfMode": controls.AfModeEnum.Manual,  # Disable autofocus
    "LensPosition": 3.2                    # Adjust this value as needed (range: 0.0 - ~10.0)
})

picam2.start()

```


set manual focus using picamera2
```python
from picamera2 import Picamera2
from libcamera import controls

def create_configured_camera(resolution=(640, 480), framerate=30, lens_position=3.0):
    """
    Initializes and configures the PiCamera2 with manual focus.

    Parameters:
        resolution (tuple): (width, height) of the camera output.
        framerate (int): Desired framerate.
        lens_position (float): Manual lens focus position (approx 0.0 to ~10.0).
    
    Returns:
        Picamera2: Configured camera instance.
    """
    picam2 = Picamera2()
    
    config = picam2.create_preview_configuration(
        main={"size": resolution, "format": "RGB888"},
        controls={"FrameDurationLimits": (int(1e6 / framerate), int(1e6 / framerate))}
    )
    
    picam2.configure(config)
    
    # Set manual focus
    picam2.set_controls({
        "AfMode": controls.AfModeEnum.Manual,
        "LensPosition": lens_position
    })

    picam2.start()
    return picam2

```

use it in detector code
```python
from utils.camera import create_configured_camera

self.picam2 = create_configured_camera(
    resolution=self.config['camera']['resolution'],
    lens_position=self.config['camera'].get('focus_position', 3.0)
)

```

add this to config file
```yaml
camera:
  resolution: [640, 480]
  framerate: 30
  focus_position: 8.5  # Set based on distance to bait
```

calibration script
```python
import cv2
import yaml
from pathlib import Path
from picamera2 import Picamera2
from libcamera import controls

CONFIG_PATH = "config/config.yaml"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(cfg, f)

def main():
    cfg = load_config()
    lens_position = cfg['camera'].get('focus_position', 3.0)

    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"format": "RGB888"})
    picam2.configure(config)
    picam2.start()
    picam2.set_controls({
        "AfMode": controls.AfModeEnum.Manual,
        "LensPosition": lens_position
    })

    print(f"[INFO] Starting calibration with LensPosition = {lens_position:.2f}")
    print("[←] decrease | [→] increase | [s] save | [q] quit")

    while True:
        frame = pic

```

```sh
python3 scripts/calibrate_focus.py

```