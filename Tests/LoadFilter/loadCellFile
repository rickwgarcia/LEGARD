import RPi.GPIO as GPIO
from hx711 import HX711

# Validate a single data point by filtering out invalid values and extreme outliers.
# Parameters:
#     value (int or float): The raw data point to check.
#     threshold (float): Maximum acceptable absolute value for valid data (default: 1e6).
# Returns:
#     bool: True if the data point is valid, False otherwise.
def is_valid_data(value, threshold=1e6):
    # Check if the value is valid: not equal to -1 or False, and within the threshold.
    return value not in [-1, False] and abs(value) <= threshold
    
# Calculate the Y value based on the weights of four sensors.
# The Y value represents the vertical balance or distribution of the load.
# Parameters:
#     weight (list): A list of four weight values corresponding to the four sensors.
#                    weight[0] = top-left sensor
#                    weight[1] = top-right sensor
#                    weight[2] = bottom-left sensor
#                    weight[3] = bottom-right sensor
# Returns:
#     float: The Y value, which indicates the vertical balance of the load.
def get_y_val(weight):
    a = weight[0]  # Top-left sensor weight
    b = weight[1]  # Top-right sensor weight
    c = weight[2]  # Bottom-left sensor weight
    d = weight[3]  # Bottom-right sensor weight
    # Calculate Y as the difference between the average of top sensors (a, b) 
    # and the average of bottom sensors (c, d).
    return ((a + b) / 2) - ((c + d) / 2)

# Calculate the X value based on the weights of four sensors.
# The X value represents the horizontal balance or distribution of the load.
# Parameters:
#     weight (list): A list of four weight values corresponding to the four sensors.
#                    weight[0] = top-left sensor
#                    weight[1] = top-right sensor
#                    weight[2] = bottom-left sensor
#                    weight[3] = bottom-right sensor
# Returns:
#     float: The X value, which indicates the horizontal balance of the load.
def get_x_val(weight):
    a = weight[0]  # Top-left sensor weight
    b = weight[1]  # Top-right sensor weight
    c = weight[2]  # Bottom-left sensor weight
    d = weight[3]  # Bottom-right sensor weight
    # Calculate X as the difference between the average of right sensors (b, d) 
    # and the average of left sensors (a, c).
    return ((b + c) / 2) - ((a + d) / 2)


# GPIO and HX711 setup
GPIO.setmode(GPIO.BCM)
sensors = [
    HX711(dout_pin=27, pd_sck_pin=17),  # Sensor 1 (0, 1)
    HX711(dout_pin=20, pd_sck_pin=21),  # Sensor 2 (1, 1)
    HX711(dout_pin=24, pd_sck_pin=23),  # Sensor 3 (1, 0)
    HX711(dout_pin=6, pd_sck_pin=5)     # Sensor 4 (0, 0)
]

#Calibrate
for index, hx in enumerate(sensors):
    print(f'Calibrating sensor {index + 1}...')
    hx.zero()
    reading = hx.get_data_mean(readings=200)
    calibrationWeight = 0.1
    calibrationValue = float(calibrationWeight)
    ratio = reading / calibrationValue
    hx.set_scale_ratio(ratio)
    print(f'Sensor {index + 1} calibration ratio set to {ratio}')

from statistics import StatisticsError

while True:
    scaledWeights = []
    all_valid = True

    for i in range(4):
        try:
            weight = sensors[i].get_weight_mean(readings=100)
            if is_valid_data(weight):
                scaledWeights.append(weight)
            else:
                print(f"Invalid reading from sensor {i + 1}: {weight}")
                all_valid = False
                break
        except StatisticsError as e:
            print(f"Statistics error in sensor {i + 1}: {e}")
            all_valid = False
            break
        except Exception as e:
            print(f"Error reading sensor {i + 1}: {e}")
            all_valid = False
            break

    if all_valid and len(scaledWeights) == 4:
        xVal = get_x_val(scaledWeights)
        yVal = get_y_val(scaledWeights)
        print(f'X Value: {xVal}, Y Value: {yVal}')
    else:
        print("Skipping X and Y calculation due to invalid sensor readings.")


