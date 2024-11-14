import RPi.GPIO as GPIO 
from hx711 import HX711

GPIO.setmode(GPIO.BCM)

hx = HX711(dout_pin = 24, pd_sck_pin = 23)

hx.zero()

#Read in weight
input('Place known weight on scale then press enter: ')
reading = hx.get_data_mean(readings = 100)

#Calculate value for ratio
calibrationWeight = input('Enter the known weight in grams: ')
calibrationValue = float(calibrationWeight)

#Find ratio
ratio = reading/calibrationValue
hx.set_scale_ratio(ratio)

while True:
	weight = hx.get_weight_mean()
	print(weight)
