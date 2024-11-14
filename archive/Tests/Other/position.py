import math
import numpy as np
from scipy import signal, integrate
def normalize(v, tolerance=0.00001):
    mag2 = sum(n * n for n in v)
    if mag2 > tolerance:
        mag = math.sqrt(mag2)
        v = tuple(n / mag for n in v)
    return np.array(v)

q = normalize([0.99304,-0.041992,-0.006286,-0.1098022])
r = np.array([0.12,-0.79,9.46])
n = np.array([[1-2*q[2]**2-2*q[3]**2, 2*(q[1]*q[2]+q[0]*q[3]), 2*(q[1]*q[3]-q[0]*q[2])],
             [2*(q[1]*q[2]-q[0]*q[3]), 1-2*q[1]**2-2*q[3]**2, 2*(q[2]*q[3]+q[0]*q[1])],
             [2*(q[1]*q[3]+q[0]*q[2]), 2*(q[2]*q[3]-q[0]*q[1]), 1-2*q[1]**2-2*q[2]**2]])
quatR = np.matmul(n,r)

b, a = signal.butter(5, 0.017, btype='high')
#x = np.array([quatR[0]])
#y = np.array([quatR[1]])
#z = np.array([quatR[2]])
#fx = signal.filtfilt(b, a, x, method="gust")
#fy = signal.filtfilt(b, a, y, method="gust")
#fz = signal.filtfilt(b, a, z, method="gust")
ft = signal.filtfilt(b, a, quatR, method="gust")
V = integrate.cumtrapz(ft, initial=0)
ftV = signal.filtfilt(b, a, V, method="gust")
P = integrate.cumtrapz(ftV, initial=0)

print(P)