import time
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055
from math import *
import numpy as np
import board

def normalize(v, tolerance=0.00001):
    try:
        mag2 = sum(n * n for n in v)
        if mag2 > tolerance:
            mag = sqrt(mag2)
            v = tuple(n / mag for n in v)
        return np.array(v)
    except:
        return np.array([0, 0, 0, 0])

#i2c = I2C(1)  # Device is /dev/i2c-1
i2c = I2C(1)
sensor = adafruit_bno055.BNO055_I2C(i2c, address= 41)

init = 0
start = 0
while True:
    Rad2Deg = 180/pi
    qw = sensor.quaternion[0]
    while init <= 0 or init >110:
        qw = sensor.quaternion[0]
        if qw is None:
            print("None")
        else:
            try:
                init = round(2*acos(qw)*Rad2Deg, 2)
            except: 
                print("math error")
                
    if qw is None:
        print("None")
    else:
        try:
            a = round(2*acos(qw)*Rad2Deg, 2) - init
            print(a)
        except: 
            print("math error")
            
    time.sleep(1)
    

