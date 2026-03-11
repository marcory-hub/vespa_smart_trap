
**One-line purpose:** command to get inference output from gv2 on screen
**Agent:** command to run in terminal by user
**Main Index:** [[_himax sdk]]

---

```python
python3 -c "
import serial
import time
s = serial.Serial('/dev/tty.usbmodem58FA1047631', 921600)
while True:
    print(s.read(s.in_waiting or 1).decode('utf-8', errors='replace'), end='')
    time.sleep(0.05)
"
```
