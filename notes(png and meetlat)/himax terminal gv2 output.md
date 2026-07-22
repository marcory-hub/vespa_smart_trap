
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

swift-yolo
```sh
python3 -u - <<'PY'
import serial, time

port = '/dev/tty.usbmodem58FA1047631'
s = serial.Serial(port, 921600, timeout=5)

# Wait for device to become ready (and to show MODEL)
while True:
    line = s.readline()
    if not line:
        continue
    text = line.decode('utf-8', errors='replace')
    print(text, end='')

    if '"name": "MODEL"' in text or '"is_ready": 1' in text:
        break

# Now start infinite invoke (RESULT_ONLY=1 => boxes only)
s.write(b'AT+INVOKE=-1,0,1\r')

# Continue streaming
while True:
    line = s.readline()
    if line:
        print(line.decode('utf-8', errors='replace'), end='')
PY
```