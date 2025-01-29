# hardware/mocks/mock_gpio.py
class MockGPIO:
    BCM = 'BCM'
    IN = 'IN'
    PUD_DOWN = 'PUD_DOWN'
    RISING = 'RISING'
    
    def __init__(self):
        self.callbacks = {}
    
    def setmode(self, mode):
        print(f"GPIO setmode: {mode}")
    
    def setup(self, pin, mode, pull_up_down=None):
        print(f"GPIO setup: Pin {pin}, Mode {mode}, Pull {pull_up_down}")
    
    def add_event_detect(self, pin, edge, callback=None):
        print(f"GPIO add_event_detect: Pin {pin}, Edge {edge}")
        if callback:
            self.callbacks[pin] = callback
    
    def remove_event_detect(self, pin):
        print(f"GPIO remove_event_detect: Pin {pin}")
        if pin in self.callbacks:
            del self.callbacks[pin]
    
    def cleanup(self):
        print("GPIO cleanup")
        self.callbacks.clear()
    
    def simulate_button_press(self, pin):
        """Simulate a button press event."""
        if pin in self.callbacks:
            print(f"Simulating button press on pin {pin}")
            self.callbacks[pin](pin)
    
    def output(self, pin, state):
        print(f"GPIO output: Pin {pin}, State {state}")

