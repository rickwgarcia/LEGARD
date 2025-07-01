import time
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055
from math import *
import numpy as np

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
    l = list(e)
    return np.dot(np.invert(l), s)
    
i2c = I2C(1)  # Device is /dev/i2c-1
sensor = adafruit_bno055.BNO055_I2C(i2c)

start = normalize(sensor.quaternion)
while True:
    tst = [0,0,0,0]
    quat = sensor.quaternion
    q = normalize(quat)
    print(q)
    calc = matrix(start, tst)
    try:
        #t = 2*acos(qw)
        #print(str(round(t*57.2957795131, 2)))
        print(calc)
        print()
        time.sleep(1)
    except:
        #qw = 1
        #t = 2*acos(qw)
        #print(str(round(t*57.2957795131, 2)))
        print()
        time.sleep(1)
        

