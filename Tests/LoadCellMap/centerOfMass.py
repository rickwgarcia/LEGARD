import RPi.GPIO as GPIO
from hx711 import HX711
from statistics import StatisticsError
import threading

def is_valid_data(value, threshold=1e6):
    """Check if a single data point is valid."""
    return value not in [-1, False] and value >= 0 and abs(value) <= threshold

def calculate_xy(weights):
    """Calculate X and Y values based on the weights of four sensors."""
    W1, W2, W3, W4 = weights
    W_total = W1 + W2 + W3 + W4
    if W_total == 0:
        return 0, 0  # Avoid division by zero

    x = ((W2 + W4) - (W1 + W3)) / W_total
    y = ((W3 + W4) - (W1 + W2)) / W_total
    return x, y

GPIO.setmode(GPIO.BCM)

# Initialize sensors
sensors = [
    HX711(dout_pin=27, pd_sck_pin=17),  # Sensor 1
    HX711(dout_pin=20, pd_sck_pin=21),  # Sensor 2
    HX711(dout_pin=24, pd_sck_pin=23),  # Sensor 3
    HX711(dout_pin=6, pd_sck_pin=5)     # Sensor 4
]

# Shared calibration ratios
calibration_ratios = [None] * len(sensors)

# Function to calibrate a single sensor
def calibrate_sensor(sensor, index):
    """Calibrate an individual sensor."""
    try:
        print(f"Calibrating sensor {index + 1}...")
        sensor.zero()
        reading = sensor.get_data_mean(readings=100)
        calibrationWeight = input(f"Enter the known weight for sensor {index + 1} in grams: ")
        calibrationValue = float(calibrationWeight)
        ratio = reading / calibrationValue
        sensor.set_scale_ratio(ratio)
        calibration_ratios[index] = ratio
        print(f"Sensor {index + 1} calibration ratio set to {ratio}")
    except Exception as e:
        print(f"Error calibrating sensor {index + 1}: {e}")

# Create and start threads for each sensor
threads = []
for i, hx in enumerate(sensors):
    thread = threading.Thread(target=calibrate_sensor, args=(hx, i))
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()

print("Calibration completed for all sensors.")

# Main loop to read, validate, convert to X and Y, and save to file
output_file = "xy_values.txt"  # Output file to save X and Y values

while True:
    scaled_weights = []
    all_valid = True

    for i, hx in enumerate(sensors):
        try:
            weight = hx.get_weight_mean()
            if is_valid_data(weight):
                scaled_weights.append(weight)
                print(f"Sensor {i + 1} weight: {weight}")
            else:
                print(f"Sensor {i + 1} invalid data: Negative, false, or extreme outlier. Skipping.")
                all_valid = False
                break
        except StatisticsError as e:
            print(f"Sensor {i + 1} StatisticsError: {e}. Skipping this reading.")
            all_valid = False
            break
        except Exception as e:
            print(f"Sensor {i + 1} Error: {e}. Skipping this reading.")
            all_valid = False
            break

    # Only proceed if all readings are valid
    if all_valid and len(scaled_weights) == 4:
        x_val, y_val = calculate_xy(scaled_weights)
        print(f"X Value: {x_val}, Y Value: {y_val}")

        # Save X and Y values to file
        with open(output_file, "a") as file:
            file.write(f"{x_val}, {y_val}\n")
    else:
        print("Skipping calculations due to invalid sensor data.")

