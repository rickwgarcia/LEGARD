import RPi.GPIO as GPIO
from hx711 import HX711

GPIO.setmode(GPIO.BCM)

hx = HX711(dout_pin = 6, pd_sck_pin = 5)

hx.zero()

#Take in readings
input('Place known weight on scale and press enter: ')
print('Reading...')
reading = hx.get_data_mean(readings = 100)

#Using known wieght start calibration
calibrationWeight = input('Enter the known weight in grams: ')
calibrationWeightVal = float(calibrationWeight)

#Define ratio
ratio = reading / calibrationWeightVal;
hx.set_scale_ratio(ratio)

while True:
    weight = hx.get_weight_mean()
    print(weight)
