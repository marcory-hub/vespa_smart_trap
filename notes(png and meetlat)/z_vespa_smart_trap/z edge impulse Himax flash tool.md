
**One-line purpose:** edge impulse
**Short summary:** 
**Agent:** archive

---

to continue project
cd naar folder
```sh
cd /Users/md/Developer/vespCVacc/accEdgeImpulse
```
source venv
```sh
source venv/bin/activate
```

---
# Himax flash tool install
2025-08-16
- Downloaded [Edge Impuls pre-compiled firmware](https://cdn.edgeimpulse.com/firmware/seeed-grove-vision-ai-module-v2.zip)
	- README
```txt
Flashing instruction:
1. Connect your board
2. Install the flashing script dependencies:

    pip install -r xmodem/requirements.txt

3. Find the serial port number or path
4. Flash firmware and model file (replace YOUR_BOARD_SERIAL PORT with the proper port number/path)

    python3 xmodem/xmodem_send.py --port=YOUR_BOARD_SERIAL --baudrate=921600 --protocol=xmodem --file=firmware.img --model="model_vela.tflite 0x200000 0x00000"

For more details on how to use this firmware, see the tutorial:
https://docs.edgeimpulse.com/docs/edge-ai-hardware/mcu-+-ai-accelerators/himax-seeed-grove-vision-ai-module-v2-wise-eye-2

```
- folder maken accEdgeImpulse en cd into folder
```sh
cd /Users/md/Developer/vespCVacc/accEdgeImpulse
```
- ZIP uitpakken: /Users/md/Developer/vespCVacc/accEdgeImpulse/seeed-grove-vision-ai-module-v2.zip
- venv maken
- source venv
- flash firmware algemene command
```sh
python3 xmodem/xmodem_send.py --port=YOUR_BOARD_SERIAL --baudrate=921600 --protocol=xmodem --file=firmware.img --model="model_vela.tflite 0x200000 0x00000"
```
- flash aangepast met
	-  usbmodem58FA1047631
```sh
python3 xmodem/xmodem_send.py --port=/dev/tty.usbmodem58FA1047631 --baudrate=921600 --protocol=xmodem --file=firmware.img
```


[Edge Impulse firmware for Seeed Grove Vision AI Module V2 (Himax WiseEye2)](https://github.com/edgeimpulse/firmware-seeed-grove-vision-ai-module-v2)
