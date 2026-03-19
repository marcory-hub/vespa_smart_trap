import serial

port = '/dev/tty.usbmodem58FA1047631'
s = serial.Serial(port, 921600, timeout=5)

s.write(b'AT+INVOKE=-1,0,1\r')  # infinite invoke, RESULT_ONLY=1 (no image)

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