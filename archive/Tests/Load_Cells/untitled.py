import RPi.GPIO as GPIO
from hx711 import HX711

GPIO.setmode(GPIO.BCM)

# List of HX711 configurations for your four sensors
sensors = [
    HX711(dout_pin=27, pd_sck_pin=17),
    HX711(dout_pin=20, pd_sck_pin=21),
    HX711(dout_pin=24, pd_sck_pin=23),
    HX711(dout_pin=6, pd_sck_pin=5)
]

# List to store calibration ratios for each sensor
calibration_ratios = []

# Calibrate each sensor
for index, hx in enumerate(sensors):
    hx.zero()
    
    reading = hx.get_data_mean(readings=100)
    calibrationWeight = 20
    calibrationValue = float(calibrationWeight)

    # Find ratio
    ratio = reading / calibrationValue
    hx.set_scale_ratio(ratio)
    calibration_ratios.append(ratio)
    print(f'Sensor {index + 1} calibration ratio set to {ratio}')

# Continuously read weights from all sensors
try:
    while True:
        for index, hx in enumerate(sensors):
            weight = hx.get_weight_mean()
            print(f'Weight from sensor {index + 1}: {weight}')
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()
