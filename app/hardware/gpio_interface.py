# hardware/gpio_interface.py
import platform
from hardware.mocks.mock_gpio import MockGPIO

try:
    if platform.system() == "Linux" and 'arm' in platform.machine():
        import RPi.GPIO as GPIO
    else:
        GPIO = MockGPIO()
except ImportError:
    from hardware.mocks.mock_gpio import MockGPIO
    GPIO = MockGPIO()

class GPIOInterface:
    def __init__(self):
        self.GPIO = GPIO
        self.GPIO.setmode(self.GPIO.BCM)
    
    def setup_pin(self, pin, mode, pull_up_down=None):
        self.GPIO.setup(pin, mode, pull_up_down)
    
    def add_event_detect(self, pin, edge, callback=None):
        self.GPIO.add_event_detect(pin, edge, callback)
    
    def remove_event_detect(self, pin):
        self.GPIO.remove_event_detect(pin)
    
    def cleanup(self):
        self.GPIO.cleanup()
    
    def simulate_button_press(self, pin):
        if isinstance(self.GPIO, MockGPIO):
            self.GPIO.simulate_button_press(pin)

