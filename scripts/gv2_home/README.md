## GV2 Home (Mac mini)

Runs on macOS with GV2 connected directly over USB serial. Plays a chime when a class is detected and saves JPEGs at 2 images/sec while confidence \u2265 0.3.

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install pyserial
```

### Run

```bash
python3 experiments/gv2_home/detect_chime_save.py --port /dev/cu.usbmodemXXXX --baudrate 921600
```

### Output

Images are saved to `experiments/gv2_home/images/` as:

`YYYYmmdd_HHMMSS_mmm_<class>_<conf>.jpg`

