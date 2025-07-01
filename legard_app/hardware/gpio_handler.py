# legard_app/hardware/gpio_handler.py

import RPi.GPIO as GPIO
from config import GPIO_MODE, PINS

class GPIOHandler:
    """Manages all GPIO pin interactions."""
    def __init__(self):
        try:
            GPIO.setmode(GPIO_MODE)
            self.is_ready = True
        except RuntimeError as e:
            print(f"Error initializing GPIO: {e}")
            print("Running in dummy mode. GPIO events will not work.")
            self.is_ready = False
            
    def setup_pins_for_stretch_selection(self, callback_map):
        """Sets up all 10 pins for initial max stretch selection."""
        if not self.is_ready: return
        
        for pin_name, pin_num in PINS.items():
            GPIO.setup(pin_num, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            if pin_name in callback_map:
                # Add a 300ms bouncetime to prevent multiple triggers
                GPIO.add_event_detect(
                    pin_num, GPIO.RISING, 
                    callback=callback_map[pin_name], 
                    bouncetime=300
                )

    def setup_pins_for_routine(self, pin_map, callback_map):
        """Sets up the specific pins needed for the exercise routine."""
        if not self.is_ready: return
        
        self.cleanup() # Clean previous event detects
        GPIO.setmode(GPIO_MODE) # Re-set mode after cleanup
        
        for name, pin_num in pin_map.items():
             GPIO.setup(pin_num, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
             if name in callback_map:
                GPIO.add_event_detect(
                    pin_num, GPIO.RISING, 
                    callback=callback_map[name],
                    bouncetime=300
                )

    def cleanup(self):
        """Cleans up all GPIO resources."""
        if not self.is_ready: return
        
        print("Cleaning up GPIO pins.")
        # Attempt to remove detection from all known pins
        for pin_num in PINS.values():
            try:
                GPIO.remove_event_detect(pin_num)
            except RuntimeError:
                pass # Ignore if event was not set up
        GPIO.cleanup()
