#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import RPi.GPIO as GPIO
from hx711 import HX711
from statistics import StatisticsError
import threading
import os, time

# --- Config ---
FILE = "/home/si/Desktop/LEGARD/Tests/RealTime/coordinates.txt"
BINS = (101, 101)
RANGE = [[-50, 50], [-50, 50]]

# --- GPIO Setup ---
GPIO.setmode(GPIO.BCM)

# Initialize HX711 sensors
sensors = [
    HX711(dout_pin=27, pd_sck_pin=17),
    HX711(dout_pin=20, pd_sck_pin=21),
    HX711(dout_pin=24, pd_sck_pin=23),
    HX711(dout_pin=16, pd_sck_pin=12)
]

calibration_ratios = [None] * len(sensors)

# --- Calibration Function ---
def calibrate_sensor(sensor, index):
    try:
        print(f"Calibrating sensor {index + 1}...")
        sensor.zero()
        reading = sensor.get_data_mean(readings=100)
        calibrationWeight = input(f"Enter known weight for sensor {index + 1} in grams: ")
        ratio = reading / float(calibrationWeight)
        sensor.set_scale_ratio(ratio)
        calibration_ratios[index] = ratio
        print(f"Sensor {index + 1} ratio set to {ratio}")
    except Exception as e:
        print(f"Calibration error on sensor {index + 1}: {e}")

# --- Sensor Utility ---
def is_valid_data(value, threshold=1e6):
    return value not in [-1, False] and value >= 0 and abs(value) <= threshold

def calculate_xy(weights):
    W1, W2, W3, W4 = weights
    total = W1 + W2 + W3 + W4
    if total == 0:
        return 0, 0
    x = ((W2 + W4) - (W1 + W3)) / total
    y = ((W3 + W4) - (W1 + W2)) / total
    return x * 50, y * 50  # scale to -50 to 50

# --- Calibration Phase ---
threads = [threading.Thread(target=calibrate_sensor, args=(hx, i)) for i, hx in enumerate(sensors)]
[t.start() for t in threads]
[t.join() for t in threads]

# --- Start with empty file ---
open(FILE, "w").close()

# --- Data Logger Thread ---
def log_sensor_data():
    while True:
        scaled_weights = []
        all_valid = True
        for i, hx in enumerate(sensors):
            try:
                weight = hx.get_weight_mean()
                if is_valid_data(weight):
                    scaled_weights.append(weight)
                else:
                    print(f"Sensor {i + 1} invalid: {weight}")
                    all_valid = False
                    break
            except StatisticsError:
                print(f"Sensor {i + 1} stats error.")
                all_valid = False
                break
            except Exception as e:
                print(f"Sensor {i + 1} error: {e}")
                all_valid = False
                break

        if all_valid and len(scaled_weights) == 4:
            x, y = calculate_xy(scaled_weights)
            print(f"X = {x:.3f}, Y = {y:.3f}")
            with open(FILE, "a", buffering=1) as f:
                f.write(f"{x:.3f}, {y:.3f}\n")
        else:
            print("Skipping write due to invalid data.")
        time.sleep(0.5)

threading.Thread(target=log_sensor_data, daemon=True).start()

# --- Heatmap Live Plot Setup ---
fig, ax = plt.subplots(figsize=(8, 6))
im  = ax.imshow(np.zeros(BINS).T, origin='lower', extent=[-50, 50, -50, 50],
                cmap='viridis', interpolation='nearest')
sc  = ax.scatter([], [], c='red', s=100, marker='o', label='Average')
plt.colorbar(im, ax=ax, label='Frequency')
ax.set_title('Real-Time Heatmap of Foot Pressure')
ax.set_xlabel('X'); ax.set_ylabel('Y')
ax.grid(color='white', linestyle='--', linewidth=0.5); ax.legend()

def update(_):
    if not os.path.exists(FILE): return im, sc
    with open(FILE) as f:
        coords = [tuple(map(float, ln.split(', '))) for ln in f if ln.strip()]
    if not coords: return im, sc
    x, y = zip(*coords)
    heat, *_ = np.histogram2d(x, y, bins=BINS, range=RANGE)
    im.set_data(heat.T)
    sc.set_offsets([[np.mean(x), np.mean(y)]])
    return im, sc

anim.FuncAnimation(fig, update, interval=500, blit=False)
plt.show()
