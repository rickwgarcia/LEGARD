import RPi.GPIO as GPIO
from hx711 import HX711
import statistics as stat

# GPIO setup
GPIO.setmode(GPIO.BCM)

# Initialize sensors
sensors = [
    HX711(dout_pin=27, pd_sck_pin=17),  # Sensor 1
    HX711(dout_pin=20, pd_sck_pin=21),  # Sensor 2
    HX711(dout_pin=24, pd_sck_pin=23),  # Sensor 3
    HX711(dout_pin=6, pd_sck_pin=5)     # Sensor 4
]

# Function to debug raw data
def debug_sensor_data(hx, index, readings=100):
    try:
        print(f"Sensor {index + 1}: Collecting raw data...")
        raw_data = []
        
        # Collect raw data
        for _ in range(readings):
            data = hx._read()  # Directly call the low-level read function
            raw_data.append(data)
        
        # Print raw data
        print(f"Sensor {index + 1} raw data: {raw_data}")
        
        # Check data distribution
        median = stat.median(raw_data)
        deviations = [abs(d - median) for d in raw_data]
        print(f"Sensor {index + 1} median: {median}")
        print(f"Sensor {index + 1} deviations from median: {deviations}")
        
        # Check for filtering issues
        if len(raw_data) < 2:
            print(f"Sensor {index + 1} has insufficient data points!")
        else:
            stdev = stat.stdev(raw_data)
            print(f"Sensor {index + 1} standard deviation: {stdev}")

    except Exception as e:
        print(f"Sensor {index + 1} error during debugging: {e}")

# Run debugging for all sensors
for i, hx in enumerate(sensors):
    debug_sensor_data(hx, i)

