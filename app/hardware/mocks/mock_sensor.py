# hardware/mocks/mock_sensor.py
import random
import math

class MockBNO055:
    def __init__(self, *args, **kwargs):
        pass
    
    @property
    def quaternion(self):
        # Simulate quaternion data
        angle_deg = random.uniform(0, 360)
        angle_rad = math.radians(angle_deg / 2)
        qw = math.cos(angle_rad)
        return (qw, 0, 0, 0)  # Simplified for mock

