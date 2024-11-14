import time
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055
from math import *
import math
import numpy as np
from scipy import signal, integrate

def normalize(v, tolerance=0.00001):
    try:
        mag2 = sum(n * n for n in v)
        if mag2 > tolerance:
            mag = math.sqrt(mag2)
            v = tuple(n / mag for n in v)
        return np.array(v)
    except:
        return np.array([0, 0, 0, 0])

def matrix(s,e):
    l = np.array([0,0,0,0])
    return np.dot(np.invert(l), s)

i2c = I2C(1)  # Device is /dev/i2c-1
sensor = adafruit_bno055.BNO055_I2C(i2c)

start = normalize(sensor.quaternion)
while True:
    tst = [0,0,0,0]
    Acc = sensor.acceleration
    quat = sensor.quaternion
    q = normalize(quat)
    calc = matrix(start, q)
    try:
        print(q)
        print()
        time.sleep(1)
    except:
        print()
        time.sleep(1)

