# legard_app/hardware/sensor_handler.py

from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055
from math import acos, pi
from config import I2C_BUS, SENSOR_1_ADDRESS, SENSOR_2_ADDRESS

class SensorHandler:
    """Manages initialization and reading of BNO055 sensors."""
    def __init__(self):
        try:
            i2c = I2C(I2C_BUS)
            self.sensor1 = adafruit_bno055.BNO055_I2C(i2c, address=SENSOR_1_ADDRESS)
            self.sensor2 = adafruit_bno055.BNO055_I2C(i2c, address=SENSOR_2_ADDRESS)
            self.is_ready = True
        except (ValueError, RuntimeError) as e:
            print(f"Error initializing sensors: {e}")
            print("Running in dummy mode. Sensors will not be read.")
            self.sensor1 = None
            self.sensor2 = None
            self.is_ready = False

    def _get_angle_from_quat(self, quaternion):
        """Calculates angle in degrees from a quaternion."""
        if quaternion is None or quaternion[0] is None:
            return None
        try:
            # Formula from original code: 2 * acos(qw) * (180/pi)
            angle = round(2 * acos(quaternion[0]) * (180 / pi), 2)
            return angle
        except (ValueError, TypeError):
            return None

    def read_quaternions(self):
        """Reads the raw quaternion data from both sensors."""
        if not self.is_ready:
            return ((1, 0, 0, 0), (1, 0, 0, 0)) # Dummy data
            
        q1 = self.sensor1.quaternion
        q2 = self.sensor2.quaternion
        return q1, q2
        
    def read_angles(self):
        """Reads quaternions and converts them to angles."""
        q1, q2 = self.read_quaternions()
        angle1 = self._get_angle_from_quat(q1)
        angle2 = self._get_angle_from_quat(q2)
        return angle1, angle2
