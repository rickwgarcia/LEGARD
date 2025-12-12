import tkinter as tk
from tkinter import ttk, messagebox
import math
import logging
import time

# ---------------------
# File: calibration_window.py
# Author: Ricardo Garcia, ricardo.garcia@cosmiac.org
# Last Modified: 2025-12-12
# Version: 2.0.0
# ---------------------

"""
Module containing the CalibrationWindow, a Toplevel window that guides the user 
through a two-step process to zero the angle sensor and determine their maximum 
safe range of motion.
"""

class CalibrationWindow(tk.Toplevel):
    """
    A full-screen Toplevel window responsible for the sensor calibration process.

    It uses the SensorThread for angle data and the SerialThread to send 
    tare/start commands to the serial device (e.g., Wii Board).
    """
    # Constants for the progress bar's appearance and range
    BAR_MAX_ANGLE = 22  
    BAR_WIDTH = 500     
    BAR_HEIGHT = 40     

    def __init__(self, parent, sensor, shared_queue, sensor_thread, serial_thread, on_complete_callback):
        """
        Initializes the CalibrationWindow.

        Args:
            parent (tk.Tk): The main application window (Dashboard).
            sensor (object): The BNO055 sensor object.
            shared_queue (queue.Queue): The queue used for reading serial data (cleared here).
            sensor_thread (SensorThread): The active thread providing angle data.
            serial_thread (SerialThread): The active thread managing serial communication.
            on_complete_callback (callable): A function to call upon completion, 
                                            receiving the calibrated initial_angle and max_angle.
        """
        super().__init__(parent)
        self.parent = parent
        self.sensor = sensor
        
        self.shared_queue = shared_queue
        self.sensor_thread = sensor_thread
        self.serial_thread = serial_thread
        
        self.on_complete_callback = on_complete_callback

        # Calibration state variables
        self.initial_angle = None # Baseline angle while standing still
        self.max_angle = 0.0      # Maximum relative angle achieved
        self.is_tracking = False  # Flag to control the update loop

        # Window Setup
        self.title("Calibration")
        self.attributes('-fullscreen', True)
        self.bind('<Escape>', lambda e: self.on_closing())
        
        # UI Elements
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(expand=True)

        self.instruction_label = ttk.Label(
            self.main_frame,
            text="Calibrating... Please stand still!",
            font=('Helvetica', 24, 'bold'),
            wraplength=800,
            justify="center"
        )
        self.instruction_label.pack(pady=40)

        self.progress_canvas = tk.Canvas(
            self.main_frame,
            width=self.BAR_WIDTH,
            height=self.BAR_HEIGHT,
            bg='lightgrey',
            highlightthickness=0
        )

        self.max_angle_label = ttk.Label(
            self.main_frame,
            text="",
            font=('Helvetica', 36, 'bold'),
            foreground='royalblue'
        )

        button_frame = ttk.Frame(self)
        button_frame.pack(side="bottom", fill="x", pady=20)
        button_frame.columnconfigure(0, weight=1)

        self.complete_button = ttk.Button(
            button_frame,
            text="Complete Calibration",
            command=self.finish_calibration,
            style='Large.TButton'
        )
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Start the two-step process after the window loads
        self.after(100, self.start_calibration)

    def start_calibration(self):
        """
        Begins the calibration sequence by checking the sensor status and sending 
        tare/start commands to the serial device.
        """
        if not self.sensor:
            messagebox.showerror("Sensor Error", "BNO055 sensor not found. Cannot calibrate.")
            self.on_closing()
            return
        
        if self.serial_thread:
            logging.info("Sending tare command to Wii Board...")
            self.serial_thread.send('z')
            logging.info("Sending start command to Wii Board...")
            self.serial_thread.send('c')
            # Clear old queue data to start fresh for the session
            with self.shared_queue.mutex:
                self.shared_queue.queue.clear()

        self.zero_sensor()
            
    def zero_sensor(self):
        """
        Performs the first step: reading and averaging the sensor's current 
        angle (quaternion W-component) to establish the baseline `initial_angle`.
        
        It then updates the UI for the second step (Max Angle Tracking).
        """
        try:
            readings_w = []
            for _ in range(10):
                if self.sensor_thread:
                    # Reading the W-component for angle calculation
                    qw = self.sensor_thread.get_quaternion()[0]
                    readings_w.append(qw)
                time.sleep(0.02)
            
            if not readings_w:
                raise RuntimeError("Failed to get a valid reading from the sensor.")

            # Calculate the average W-component and convert it to an angle
            avg_qw = sum(readings_w) / len(readings_w)
            avg_qw = max(min(avg_qw, 1.0), -1.0) # Clamp value for math.acos
            self.initial_angle = math.acos(avg_qw) * 2 * (180 / math.pi)
            logging.info(f"Sensor zeroed. Initial angle set to: {self.initial_angle:.2f}")

            # Update UI for the next step: Max Angle Tracking
            self.instruction_label.config(text="Lift your leg as high as you can.")
            
            self.progress_canvas.pack(pady=20)
            self.max_angle_label.pack(pady=20)
            self.max_angle_label.config(text=f"Max Angle: {self.max_angle:.1f}°")
            
            self.complete_button.grid(row=0, column=0, ipady=10, ipadx=20)
            
            self.is_tracking = True
            self.track_max_angle()

        except (OSError, RuntimeError) as e:
            logging.error(f"Could not zero sensor due to an error: {e}")
            messagebox.showerror("Sensor Error", "Could not read from the angle sensor. Please close and try again.")
            self.on_closing()

    def track_max_angle(self):
        """
        The continuous loop that reads the sensor, calculates the relative angle 
        (current - initial), updates the maximum angle achieved, and redraws 
        the progress bar.
        
        This method schedules itself to run every 50ms using `self.after`.
        """
        if not self.is_tracking:
            return

        relative_angle = 0 
        try:
            if self.sensor_thread and self.initial_angle is not None:
                qw = self.sensor_thread.get_quaternion()[0]
                if qw is not None:
                    # Convert quaternion W back to absolute angle
                    qw = max(min(qw, 1.0), -1.0)
                    current_abs_angle = math.acos(qw) * 2 * (180 / math.pi)
                    # Calculate the angle relative to the initial zeroed angle
                    relative_angle = current_abs_angle - self.initial_angle
                    
                    if relative_angle > self.max_angle:
                        self.max_angle = relative_angle
                        
                    self.max_angle_label.config(text=f"Max Angle: {self.max_angle:.1f}°")
        except Exception as e:
            pass
        
        self._update_progress_bar(relative_angle, self.max_angle)
        self.after(50, self.track_max_angle)

    def _update_progress_bar(self, current_angle, max_angle):
        """
        Redraws the Tkinter canvas to visually represent the current and maximum 
        angles achieved. 
        
        The green fill represents the current angle, and the red line represents 
        the peak max angle achieved in the session.

        Args:
            current_angle (float): The current relative angle reading.
            max_angle (float): The maximum relative angle recorded so far.
        """
        self.progress_canvas.delete("all")

        # 1. Draw Green Fill (Current Angle)
        fill_ratio = current_angle / self.BAR_MAX_ANGLE
        fill_width = self.BAR_WIDTH * fill_ratio
        fill_width = max(0, min(fill_width, self.BAR_WIDTH)) # Clamp to canvas width
        
        self.progress_canvas.create_rectangle(0, 0, fill_width, self.BAR_HEIGHT, fill='mediumseagreen', outline="")

        # 2. Draw Red Marker (Max Angle)
        max_ratio = max_angle / self.BAR_MAX_ANGLE
        max_x = self.BAR_WIDTH * max_ratio
        max_x = max(0, min(max_x, self.BAR_WIDTH)) # Clamp to canvas width

        if max_x > 0:
            self.progress_canvas.create_line(max_x, 0, max_x, self.BAR_HEIGHT, fill='red', width=3)

    def finish_calibration(self):
        """
        Stops tracking, calls the external callback function with the results, 
        and closes the calibration window.
        """
        self.is_tracking = False
        self.on_complete_callback(self.initial_angle, self.max_angle)
        self.destroy()

    def on_closing(self):
        """Handles closing the window, stopping the tracking loop."""
        self.is_tracking = False
        self.destroy()