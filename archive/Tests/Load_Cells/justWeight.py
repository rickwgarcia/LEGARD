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
    print(f'Calibrating sensor {index + 1}...')
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

# Calculate the Y value based on the weights of four sensors.
def get_y_val(weight):
    a = weight[0]
    b = weight[1]
    c = weight[2]
    d = weight[3]
    return ((a + b) / 2) - ((c + d) / 2)

# Calculate the X value based on the weights of four sensors.
def get_x_val(weight):
    a = weight[0]
    b = weight[1]
    c = weight[2]
    d = weight[3]
    return ((b + d) / 2) - ((a + c) / 2)

initialWeights = []
scaledWeights = []

# Get initial weights and scale them
for index, hx in enumerate(sensors):
    initialWeight = hx.get_weight_mean()
    initialWeights.append(initialWeight)
    scaledWeight = scale_to(initialWeight, initialWeight, 1000, 0, 100)  # Fixed parameters
    scaledWeights.append(scaledWeight)

# Assuming you want to calculate xVal and yVal inside the while loop
while True:
    
    for i in range(4):  # Loop over indices
        weight = sensors[i].get_weight_mean()  # Get weight from the current sensor
        print(f'Sensor {i + 1} wieght {weight}')
        scaledWeight = scale_to(weight, initialWeights[i], 1000, 0, 100)  # Scale the weight
        scaledWeights[i] = scaledWeight  # Update the scaled weight for the current index
    
    # Calculate xVal and yVal using the scaledWeights list
    xVal = get_x_val(scaledWeights)  # Pass the entire list
    yVal = get_y_val(scaledWeights)  # Pass the entire list
    
    print(f'X Value: {xVal}, Y Value: {yVal}')  # Print the calculated values

