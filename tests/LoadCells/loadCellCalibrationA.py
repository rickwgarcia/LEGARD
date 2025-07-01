import RPi.GPIO as GPIO 
from hx711 import HX711

GPIO.setmode(GPIO.BCM)

hx = HX711(dout_pin = 27, pd_sck_pin = 17)

hx.zero()

#Read in weight
input('Place known weight on scale then press enter: ')
reading = hx.get_data_mean(readings = 1000)

#Calculate value for ratio
calibrationWeight = input('Enter the known weight in grams: ')
calibrationValue = float(calibrationWeight)

#Find ratio
ratio = reading/calibrationValue
hx.set_scale_ratio(ratio)

while True:
	try:
		weight = hx.get_weight_mean()
		if weight is False:
			print("Error reading weight: False")
		else:
			print(weight)
	except StatisticsError as e:
		print("Error calculating variance:", e)
		weight = None

	
