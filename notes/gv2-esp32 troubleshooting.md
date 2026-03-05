**One-line purpose:** esp32-s3 trouble shooting
**Short summary:** upload problem, put board in bootloader mode
**Agent:** archived, esp32-s3 is not needed with lilygo devices

---


**upload problem**
check serial ports
```sh
ls /dev/cu.*
```
Look for something like /dev/cu.usbmodem* or /dev/cu.usbserial*.

**Put Board in Bootloader Mode**
For ESP32-S3:
1. Hold the BOOT button (tiny, next to the USB-C)
2. Press and release the RESET button (tiny, next to other side of the USB-C)
3. Release the BOOT button
4. Upload immediately (within a few seconds)

