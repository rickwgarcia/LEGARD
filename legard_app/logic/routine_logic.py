# legard_app/logic/routine_logic.py

import time
from math import pi
from itertools import count
from hardware.sensor_handler import SensorHandler

class RoutineLogic:
    """
    Handles the real-time calculations and logic during an exercise routine.
    This class is designed to be run in a separate process.
    """
    def __init__(self, shared_state):
        self.state = shared_state
        self.sensors = SensorHandler()
        self.time_stepper = count()

    def run(self):
        """The main loop for the routine process."""
        self._initialize_angles()

        while self.state['running']:
            if self.state['paused_for_rest']:
                self._handle_rest_period()
            else:
                self._handle_active_repetition()
            time.sleep(1) # Main loop delay

    def _initialize_angles(self):
        """Waits for valid initial angle readings from sensors."""
        print("Initializing sensor angles...")
        initial_angle1, initial_angle2 = None, None
        while initial_angle1 is None or initial_angle2 is None:
            if not self.state['running']: return # Exit if stopped
            initial_angle1, initial_angle2 = self.sensors.read_angles()
            if initial_angle1 is not None and (initial_angle1 <= 0 or initial_angle1 > 150): initial_angle1 = None
            if initial_angle2 is not None and (initial_angle2 <= 0 or initial_angle2 > 150): initial_angle2 = None
            time.sleep(0.1)
        
        self.state['initial_angle1'] = initial_angle1
        self.state['initial_angle2'] = initial_angle2
        print(f"Initial angles set: {initial_angle1}, {initial_angle2}")

    def _handle_active_repetition(self):
        """Processes sensor data during an active rep."""
        q1, q2 = self.sensors.read_quaternions()
        
        # We need to calculate current relative angles
        # This part is complex and needs to replicate original logic carefully
        # For now, let's just log data points
        current_time = next(self.time_stepper)
        angle1, angle2 = self.sensors.read_angles()

        rel_angle1 = 0
        rel_angle2 = 0

        if self.state['rep_in_progress']:
            if angle1 is not None:
                rel_angle1 = angle1 - self.state['initial_angle1']
            if angle2 is not None:
                rel_angle2 = angle2 - self.state['initial_angle2']
            
            # Update max angle for the current rep
            if rel_angle1 > self.state['current_rep_max_angle']:
                self.state['current_rep_max_angle'] = rel_angle1

        # Append data for plotting
        self.state['x_data'].append(current_time)
        self.state['y1_data'].append(rel_angle1)
        self.state['y2_data'].append(rel_angle2)
        
        # Check for stretch failure (velocity too low for too long)
        # This logic was complex in the original file and can be refined here.

    def _handle_rest_period(self):
        """Handles the logic during a rest period between sets."""
        self.state['x_data'].append(next(self.time_stepper))
        self.state['y1_data'].append(0)
        self.state['y2_data'].append(0)

        elapsed_rest_time = time.time() - self.state['rest_start_time']
        remaining_time = self.state['total_rest_time'] - elapsed_rest_time

        if remaining_time <= 0:
            self.state['paused_for_rest'] = False
            self.state['current_set'] += 1
            self.state['message'] = "Rest over. Continue routine."
        else:
            minutes, seconds = divmod(int(remaining_time), 60)
            self.state['message'] = f"Resting... {minutes:02d}:{seconds:02d} remaining"
