import RPi.GPIO as GPIO
from hx711 import HX711
import tkinter as tk

# GPIO and HX711 setup
GPIO.setmode(GPIO.BCM)
sensors = [
    HX711(dout_pin=27, pd_sck_pin=17),  # Sensor 1 (0, 1)
    HX711(dout_pin=20, pd_sck_pin=21),  # Sensor 2 (1, 1)
    HX711(dout_pin=24, pd_sck_pin=23),  # Sensor 3 (1, 0)
    HX711(dout_pin=6, pd_sck_pin=5)     # Sensor 4 (0, 0)
]

# Calibration
calibration_ratios = []
for index, hx in enumerate(sensors):
    hx.zero()
    reading = hx.get_data_mean(readings=100)
    calibrationWeight = 0.1
    calibrationValue = float(calibrationWeight)
    ratio = reading / calibrationValue
    hx.set_scale_ratio(ratio)
    calibration_ratios.append(ratio)
    print(f'Sensor {index + 1} calibration ratio set to {ratio}')

# Function to re-map a number from one range to another.
def scale_to(val, fromLow, fromHigh, toLow, toHigh):
    return (val - fromLow) * (toHigh - toLow) / (fromHigh - fromLow) + toLow

initialWeights = []
scaledWeights = []

# Get initial weights and scale them
for index, hx in enumerate(sensors):
    initialWeight = hx.get_weight_mean()
    initialWeights.append(initialWeight)
    scaledWeight = scale_to(initialWeight, initialWeight, 1000, 0, 100)  # Fixed parameters
    scaledWeights.append(scaledWeight)

# Print the lengths of scaled and initial weights
sw = len(scaledWeights)
iw = len(initialWeights)
print(f'Length of scaled / initial: {sw} {iw}')

while True:
    print(scaledWeights)  # Print the updated scaled weights for verification
    for i in range(4):  # Corrected range to loop over indices
        weight = sensors[i].get_weight_mean()  # Corrected to use the sensors list
        scaledWeight = scale_to(weight, initialWeights[i], 1000, 0, 100)  # Fixed parameters
        scaledWeights[i] = scaledWeight  # Update the scaled weight for the current index
