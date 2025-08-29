import RPi.GPIO as GPIO
from hx711 import HX711
from statistics import StatisticsError

# Validate a single data point by filtering out invalid values, negatives, and extreme outliers.
# Parameters:
#     value (int or float): The raw data point to check.
#     threshold (float): Maximum acceptable absolute value for valid data (default: 1e6).
# Returns:
#     bool: True if the data point is valid, False otherwise.
def is_valid_data(value, threshold=1e6):
    # Check if the value is valid: not -1, not False, not negative, and within the threshold.
    return value not in [-1, False] and value >= 0 and abs(value) <= threshold

GPIO.setmode(GPIO.BCM)

# Initialize the sensor (Sensor 3 in this case)
hx = HX711(dout_pin=24, pd_sck_pin=23)

hx.zero()

# Read in weight for calibration
input('Place known weight on scale then press Enter: ')
reading = hx.get_data_mean(readings=100)

# Calculate value for ratio
calibrationWeight = input('Enter the known weight in grams: ')
calibrationValue = float(calibrationWeight)

# Find and set ratio
ratio = reading / calibrationValue
hx.set_scale_ratio(ratio)

# Main loop to read and filter weight
while True:
    try:
        weight = hx.get_weight_mean()
        if is_valid_data(weight):
            print(weight)
        else:
            print(f"InvalidData: Neagative, false or extreme outlier. Skipping this reading.")
    except StatisticsError as e:
        print(f"StatisticsError: {e}. Skipping this reading.")
    
