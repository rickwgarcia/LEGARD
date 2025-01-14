import RPi.GPIO as GPIO
import time

ButtonPin = 16
GPIO.setmode(GPIO.BCM)

def button(channel):
    print('yes')


GPIO.setup(ButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(ButtonPin, GPIO.RISING, callback=button, bouncetime=100)

try:
    while True:
        time.sleep(0.01)
except KeyboardInterrupt:
    GPIO.cleanup()