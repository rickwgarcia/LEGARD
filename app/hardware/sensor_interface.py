# hardware/sensor_interface.py
import platform
from hardware.mocks.mock_sensor import MockBNO055

try:
    if platform.system() == "Linux" and 'arm' in platform.machine():
        import adafruit_bno055
        from adafruit_extended_bus import ExtendedI2C as I2C
    else:
        adafruit_bno055 = MockBNO055
        I2C = object  # Dummy placeholder
except ImportError:
    from hardware.mocks.mock_sensor import MockBNO055
    adafruit_bno055 = MockBNO055
    I2C = object  # Dummy placeholder

class SensorInterface:
    def __init__(self, address=0x28):
        self.i2c = I2C(1)  # Device is /dev/i2c-1
        self.sensor = adafruit_bno055.BNO055_I2C(self.i2c, address=address)
    
    def get_quaternion(self):
        return self.sensor.quaternion

