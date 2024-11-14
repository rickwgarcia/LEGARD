import time
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055
from math import *
import numpy as np

def normalize(v, tolerance=0.00001):
    try:
        mag2 = sum(n * n for n in v)
        if mag2 > tolerance:
            mag = sqrt(mag2)
            v = tuple(n / mag for n in v)
        return np.array(v)
    except:
        return np.array([0, 0, 0, 0])

i2c = I2C(1)  # Device is /dev/i2c-1
sensor = adafruit_bno055.BNO055_I2C(i2c)

while True:
    print("Gyroscope (rad/sec): {}".format(sensor.gyro))
    #print("Linear acceleration (m/s^2): {}".format(sensor.linear_acceleration))
    time.sleep(1)

