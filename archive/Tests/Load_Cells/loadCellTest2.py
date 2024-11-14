import RPi.GPIO as GPIO
from hx711 import HX711

GPIO.setmode(GPIO.BCM)

hx = HX711(dout_pin=6, pd_sck_pin=5)

hx.zero()

input('Place weith and press Enter: ')
reading = hx.get_data_mean(readings=100)

known_weight = input('Enter known weight in pounds and press Enter: ')
value = float(known_weight)

ratio = reading/value
ratio2 = -2900
hx.set_scale_ratio(ratio2)
print("Calculated ratio = " + str(ratio))
while True:
    weight = hx.get_weight_mean()
    print(weight)
