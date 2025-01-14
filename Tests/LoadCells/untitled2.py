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

# Create the GUI window
root = tk.Tk()
root.title("Weight Distribution Drift with Dense Grid")
canvas_size = 300
canvas = tk.Canvas(root, width=canvas_size, height=canvas_size, bg='white')
canvas.pack()

# Initial dot position (centered)
dot_size = 10
dot_x = (canvas_size - dot_size) // 2
dot_y = (canvas_size - dot_size) // 2

# Function to draw a dense grid
def draw_grid():
    grid_size = 25  # Size of each grid cell (smaller size)
    for i in range(0, canvas_size, grid_size):
        canvas.create_line(i, 0, i, canvas_size, fill='lightgray')
        canvas.create_line(0, i, canvas_size, i, fill='lightgray')

# Function to update the dot position
def update_dot_position():
    global dot_x, dot_y
    
    weights = []
    for hx in sensors:
        weight = hx.get_weight_mean()
        weights.append(weight)

    # Determine the direction of the most weight
    max_weight_index = weights.index(max(weights))
    
    # Move dot based on the most weight
    if max_weight_index == 0:  # Sensor 1
        dot_x += 25  # Move more to see changes clearly
        dot_y -= 25
    elif max_weight_index == 1:  # Sensor 2
        dot_x += 25
        dot_y += 25
    elif max_weight_index == 2:  # Sensor 3
        dot_x -= 25
        dot_y += 25
    elif max_weight_index == 3:  # Sensor 4
        dot_x -= 25
        dot_y -= 25

    # Keep dot within bounds
    dot_x = max(min(dot_x, canvas_size - dot_size), 0)
    dot_y = max(min(dot_y, canvas_size - dot_size), 0)

    # Redraw the canvas
    canvas.delete("all")
    draw_grid()  # Draw the dense grid
    canvas.create_oval(dot_x, dot_y, dot_x + dot_size, dot_y + dot_size, fill='blue')
    
    # Schedule the next update
    root.after(1000, update_dot_position)  # Update every second

# Start drawing the grid and updating the dot position
draw_grid()
update_dot_position()

# Run the GUI main loop
try:
    root.mainloop()
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()
