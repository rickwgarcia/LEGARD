import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import RPi.GPIO as GPIO
from hx711 import HX711
import time

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
    reading = hx.get_data_mean(readings=20)
    calibrationWeight = 0.1  # Known calibration weight in kg
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

# Initialize weight lists
initialWeights = []
scaledWeights = [0, 0, 0, 0]

# Get initial weights and scale them
for index, hx in enumerate(sensors):
    initialWeight = hx.get_weight_mean()
    initialWeights.append(initialWeight)
    scaledWeight = scale_to(initialWeight, initialWeight, 1000, 0, 100)  # Fixed parameters
    scaledWeights[index] = scaledWeight

# Data for plotting
x_data = []
y_data = []

# Create figure and axis
fig, ax = plt.subplots()
sc = ax.scatter(x_data, y_data)
ax.set_xlim(-50, 50)  # Adjust limits based on your weight distribution range
ax.set_ylim(-50, 50)
ax.set_xlabel("X-axis")
ax.set_ylabel("Y-axis")
ax.set_title("Weight Distribution Graph")

# Function to update the scatter plot
def update(frame):
    global scaledWeights, x_data, y_data
    
    # Update weights from sensors
    for i in range(4):  # Loop over indices
        weight = sensors[i].get_weight_mean()  # Get weight from the current sensor
        scaledWeight = scale_to(weight, initialWeights[i], 1000, 0, 100)  # Scale the weight
        scaledWeights[i] = scaledWeight  # Update the scaled weight for the current index
    
    # Calculate xVal and yVal using the scaledWeights list
    xVal = get_x_val(scaledWeights)  # Pass the entire list
    yVal = get_y_val(scaledWeights)  # Pass the entire list
    
    
	#print for testing
    print(f'X Value: {xVal}, Y Value: {yVal}')  # Print the calculated values
    
    # Append the new values to the data lists
    x_data.append(xVal)
    y_data.append(yVal)
    
    # Update scatter plot data
    sc.set_offsets(np.c_[x_data, y_data])
    return sc,

# Animation
ani = FuncAnimation(fig, update, interval=500, blit=True)

# Show plot
plt.show()

# Cleanup GPIO on exit
def cleanup():
    GPIO.cleanup()

import atexit
atexit.register(cleanup)
