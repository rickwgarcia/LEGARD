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
    print(1)
    hx.zero()
    reading = hx.get_data_mean(readings=100)
    calibrationWeight = 0.1
    calibrationValue = float(calibrationWeight)
    ratio = reading / calibrationValue
    hx.set_scale_ratio(ratio)
    calibration_ratios.append(ratio)
    print(f'Sensor {index + 1} calibration ratio set to {ratio}')

weights = []

for index, hx in enumerate(sensors):
    weight = hx.get_weight_mean()
    weights.append(weight)



while True:
    for i in range(4):  # Corrected range to loop over indices
        try:
            weight = sensors[i].get_weight_mean()  # Corrected to use the sensors list
            if weight is False:
                print("Error reading weight: False")
            else:
                weights[i] = weight # Update the scaled weight for the current index
                print(f'{i}: {weight}')  # Print the calculated values
        except StatisticsError as e:
            print("Error calculating variance:", e)
            weight = None
