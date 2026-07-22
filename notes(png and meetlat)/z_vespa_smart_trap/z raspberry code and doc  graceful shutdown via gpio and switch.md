**One-line purpose:** online examples for graceful shutdown
**Short summary:** shutdown via switch and gpio
**Agent:** archived

---

https://learn.sparkfun.com/tutorials/raspberry-pi-safe-reboot-and-shutdown-button/all#:~:text=The%20following%20example%20loads%20a,connected%20to%20GPIO17%20is%20pressed.
niet op pi5?

https://roboticsbackend.com/raspberry-pi-gpio-interrupts-tutorial/

https://dev.to/stephaniecodes/build-a-safe-way-to-shutdown-a-headless-raspberry-pi-with-a-tiny-button-2ca3

https://raspberrypi.stackexchange.com/questions/117013/raspberry-pi-4-b-gpio-boot-and-shutdown-buttons


```python
import RPi.GPIO as GPIO
import time
import os

# Define the GPIO pin connected to the switch
SHUTDOWN_PIN = 27  # Example pin, change as needed

# Set the GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(SHUTDOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Use pull-up resistor

def shutdown_callback(channel):
    print("Shutdown button pressed!")
    os.system("sudo shutdown -h now")

try:
    GPIO.add_event_detect(SHUTDOWN_PIN, GPIO.FALLING, callback=shutdown_callback, bouncetime=300)
    print("Shutdown script running. Press the button to shut down.")
    while True:
        time.sleep(1)  # Keep the script running and listening for button presses
except KeyboardInterrupt:
    print("Exiting gracefully.")
finally:
    GPIO.cleanup()


```