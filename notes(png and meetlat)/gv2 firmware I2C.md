GV2 exposes an I2C slave at address `0x63`

gv2 returns 1 byte:
- `0x00` = no detection
- `0x01` = hornet (class 3)
- `0x02` = other class

the ESP32:
- Poll I2C address `0x63`
- Read 1 byte
- Turn LEDs on/off immediately based on that byte
- Slow I2C to 100 kHz to make it stable on your wiring.

LED:
GPIO 2: red (class 3 asian hornet)
GPIO 3: yellow
GPIO 4: green
yellow led blinks 3 times when 
powering on to check the connection

I2C speed is reduced to 100 kHz, it was not always recived by the ESP32 (some dropped detections).