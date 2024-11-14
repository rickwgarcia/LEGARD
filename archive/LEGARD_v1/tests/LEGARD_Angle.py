import time
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055
from math import *

# To enable i2c-gpio, add the line `dtoverlay=i2c-gpio` to /boot/config.txt
# Then reboot the pi
# Create library object using our Extended Bus I2C port
# Use `ls /dev/i2c*` to find out what i2c devices are connected
i2c = I2C(1)  # Device is /dev/i2c-1
sensor = adafruit_bno055.BNO055_I2C(i2c)

while True:
    qw = sensor.quaternion[0]
    r = 10
    try:
        a = round(2*acos(qw)*57.2957795131, 2)
        if a < 5:
            a=0
        print(str(a)+" ^o")
        p = round(2*pi*r*(a/360), 2)
        print(str(p)+" cm")
        print()
        time.sleep(1)
    except:
        qw = 1
        a = round(2*acos(qw)*57.2957795131, 2)
        print(str(a)+" ^o")
        p = round(2*pi*r*(a/360), 2)
        print(str(p)+" cm")
        print()
        time.sleep(1)
