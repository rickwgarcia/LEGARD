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

i2c = I2C(1)  # Device is /dev/i2c-1
sensor = adafruit_bno055.BNO055_I2C(i2c)



while True:
    Acc = sensor.acceleration
    quat = sensor.quaternion
    q = normalize(quat)
    print(q)
    r = np.array(Acc)
    n = np.array([[1-2*q[2]**2-2*q[3]**2, 2*(q[1]*q[2]+q[0]*q[3]), 2*(q[1]*q[3]-q[0]*q[2])],
                 [2*(q[1]*q[2]-q[0]*q[3]), 1-2*q[1]**2-2*q[3]**2, 2*(q[2]*q[3]+q[0]*q[1])],
                 [2*(q[1]*q[3]+q[0]*q[2]), 2*(q[2]*q[3]-q[0]*q[1]), 1-2*q[1]**2-2*q[2]**2]])
    try:
        quatR = np.matmul(n,r)
    except:
        quatR = np.array([0, 0, 0])
    b, a = signal.butter(5, 0.017, btype='high')
    ft = signal.filtfilt(b, a, quatR, method="gust")
    V = integrate.cumtrapz(ft, initial=0)
    ftV = signal.filtfilt(b, a, V, method="gust")
    P = integrate.cumtrapz(ftV, initial=0)
    if P[2] < 1.5:
        print("0 cm")
    else:
        print(str(P[2]*2.75)+ " cm")
    
    time.sleep(1)
