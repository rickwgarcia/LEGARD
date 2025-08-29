import RPi.GPIO as GPIO 
from hx711 import HX711

GPIO.setmode(GPIO.BCM)

hx = HX711(dout_pin = 20, pd_sck_pin = 21)


#Find ratio
ratio =  5260

while True:
	weight = hx.get_weight_mean()
	print(weight)
