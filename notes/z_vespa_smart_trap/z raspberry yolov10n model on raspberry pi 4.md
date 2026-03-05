
**One-line purpose:** documentation how to run yolo11n model on raspberry pi4
**Short summary:** 
**Agent:** archived

---

# Prepare Raspberry Pi4

Use Raspberry Pi Imager to install bookworm 64gb on your SD card
Raspberry Pi Model: Raspberry Pi 4
Operating System: Raspberry Pi OS (64-bit)
Edit settings to preconfigure:
hostname: vespcv
username: detector
password: `*****`
and the other options
Detailed information can be found [here](https://www.raspberrypi.com/documentation/computers/getting-started.html)

# 1. (Optioneel) maak connect via SSH of connect
[[rpi connect]]
[[rpi SSH]]

# 2. Virtuele omgeving
Maak folder vespCV
[[virtual environment maken]] .venv

```sh
source vespCV-env/bin/activate
```

# 3. Install dependencies and yolo repro
```sh
sudo apt update
sudo apt install python3-opencv
```

```shell
pip3 install torch torchvision ultralytics
```

```sh
sudo apt install libcamera-dev
```
Clone the yolov10 repository
```sh
git clone https://github.com/THU-MIG/yolov10.git
```
cd into the directory
```sh
cd yolov10
```
Install the packages
```sh
pip install .
```

```sh
pip install huggingface-hub
```

[[Install pytorch on bookworm]]
# 4. 16mp IMX519 CSI camera Arducam on bookworm
[[rpi arducam 16MP IMX519 CSI camera]]
[[rpi arduino CSI camera test]]
# 5. hornet3000 python code
Slideshow maken met foto's app ca 30 seconden
## Code op mac mini
[[z raspberry local code testSlideshowImages mac]]
[[z raspberry local code testSlideshowVideo mac]]
[[z raspberry local code testUSBCamImages mac]]
[[z raspberry local code testUSBCamVideo mac]]
## Code op raspberry pi4 bookworm
in .venv (source .venv/bin/activate)
[[z raspberry local code testSlideshowRPI rpi4]]
[[z raspberry local code testIntervalCSIcamImages rpi]]
[[libcamera-still -help]]

list USB camera
```sh
v4l2-ctl --list-devices
```


# 6. Copy python code to raspberry
copy folder contents to the raspberry
```sh
scp /path/to/local/last.pt username@raspberrypi_address:/path/to/remote/destination
```

copy from raspberry to current folder on mac
```sh
scp vespcv@192.168.2.14:/home/vespcv/vespCV/testSlider.mp4 .
```

Optional:
Bij gebruik van Geany met python3 in venv doet run button het niet. Alle python3 vervangen door path naar python3 in de venv.
Vind path door in venv terminal which python3 
```python
which python3
```
in `Build` > `Set build commands` > replace python3 with the output from which python3
[[rpi geany python3 run button]]
# 7. Make .py executable
Om in terminal met python3 de code te runnen (python3 filenaam) py bestanden eerst executable maken.
```sh
chmod +x ./vespCVtest 
```

[[rpi autorun]]