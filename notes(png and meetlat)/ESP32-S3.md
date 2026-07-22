![[ESP32-S3.png]]
ESP32-S3
GPIO5: SDA (data white cable)
GPIO6: SCL (clock yellow cable)
GPIO2: red light
GPIO4: green light

Grove vision ai v2
SDA = white cable
SCL = yellow cable

grove vision ai v2 is the slave
esp32-s3 is the master

---
flash esp32

cd to `experiments/gv2_esp32_sd/`
```sh
pio run -e esp32s3-gv2 -t upload
```

open serial monitor
```sh
pio device monitor -b 115200
```
[i2c] Found device at 0x28

new build targets I2C at 0x28 directly, and we can read out

flash and serial output
```sh
cd experiments/gv2_esp32_sd
pio run -e esp32s3-gv2 -t upload
pio device monitor -b 115200
```