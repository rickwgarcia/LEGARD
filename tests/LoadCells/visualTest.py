import RPi.GPIO as GPIO
from hx711 import HX711
import PySimpleGUI as sg
import numpy as np
import time

# Initialize GPIO and HX711
GPIO.setmode(GPIO.BCM)

# Define your HX711 load cell pins
hx1 = HX711(dout_pin=6, pd_sck_pin=5)
hx2 = HX711(dout_pin=6, pd_sck_pin=5)
hx3 = HX711(dout_pin=6, pd_sck_pin=5)
hx4 = HX711(dout_pin=6, pd_sck_pin=5)

hx1.zero()
hx2.zero()
hx3.zero()
hx4.zero()

# Set calibration for each scale
def calibrate_scale(hx, weight):
    input('Place known weight on scale then press enter: ')
    reading = hx.get_data_mean(readings=100)
    ratio = reading / weight
    hx.set_scale_ratio(ratio)

# Calibrate each scale with a known weight
calibrate_scale(hx1, float(input('Enter known weight for Scale 1 (in grams): ')))
calibrate_scale(hx2, float(input('Enter known weight for Scale 2 (in grams): ')))
calibrate_scale(hx3, float(input('Enter known weight for Scale 3 (in grams): ')))
calibrate_scale(hx4, float(input('Enter known weight for Scale 4 (in grams): ')))

# Create the GUI layout
layout = [
    [sg.Text('Weight Distribution', font=('Helvetica', 16))],
    [sg.Canvas(key='canvas')],
    [sg.Button('Exit')]
]

# Create the window
window = sg.Window('Weight Distribution', layout, finalize=True)

# Get the canvas element for drawing
canvas_elem = window['canvas']
canvas = canvas_elem.TKCanvas

# Function to draw the weight distribution
def draw_distribution(weights):
    # Clear the canvas
    canvas.delete("all")
    
    # Convert weights to a numpy array
    weights = np.array(weights)
    
    # Normalize weights for visualization
    weights = weights / np.max(weights) * 100
    
    # Define positions for the load cells
    positions = [(100, 100), (300, 100), (100, 300), (300, 300)]
    
    # Draw circles based on weight distribution
    for (x, y), weight in zip(positions, weights):
        radius = weight if weight > 0 else 1  # Avoid zero radius
        canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill='blue')
        canvas.create_text(x, y, text=f'{weight:.1f} g', fill='white')

# Event loop
try:
    while True:
        event, values = window.read(timeout=100)

        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break
        
        # Read weights from each HX711
        weight1 = hx1.get_weight_mean()
        weight2 = hx2.get_weight_mean()
        weight3 = hx3.get_weight_mean()
        weight4 = hx4.get_weight_mean()

        # Update the distribution on the canvas
        draw_distribution([weight1, weight2, weight3, weight4])

finally:
    GPIO.cleanup()
    window.close()
