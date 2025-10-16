import tkinter as tk
from tkinter import ttk, messagebox
import math
import logging

class CalibrationWindow(tk.Toplevel):
    """
    A fullscreen window for a two-step calibration process:
    1. Instantly zeroes the sensor when the window opens.
    2. Measures the maximum angle of a leg lift.
    """
    def __init__(self, parent, sensor, on_complete_callback):
        """
        Initializes the calibration window and starts the calibration immediately.

        Args:
            parent: The parent window (the Dashboard).
            sensor: The BNO055 sensor object.
            on_complete_callback: The function to call when calibration is finished.
        """
        super().__init__(parent)
        self.parent = parent
        self.sensor = sensor
        self.on_complete_callback = on_complete_callback

        # Calibration state variables
        self.initial_angle = None
        self.max_angle = 0.0
        self.is_tracking = False

        # --- Window Setup ---
        self.title("Calibration")
        self.attributes('-fullscreen', True)
        self.bind('<Escape>', lambda e: self.on_closing())
        
        # --- UI Elements ---
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
        
        self.max_angle_label = ttk.Label(
            self.main_frame,
            text="",
            font=('Helvetica', 36, 'bold'),
            foreground='royalblue'
        )
        # This will be packed later

        # Frame for the bottom button
        button_frame = ttk.Frame(self)
        button_frame.pack(side="bottom", fill="x", pady=20)
        button_frame.columnconfigure(0, weight=1)

        self.complete_button = ttk.Button(
            button_frame,
            text="Complete Calibration",
            command=self.finish_calibration,
            style='Large.TButton'
        )
        # Button is managed (hidden/shown) by the calibration logic
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start the calibration process immediately after the window is drawn
        self.after(100, self.start_calibration)

    def start_calibration(self):
        """Checks for the sensor and then performs the zeroing process."""
        if not self.sensor:
            messagebox.showerror("Sensor Error", "BNO055 sensor not found. Cannot calibrate.")
            self.on_closing()
            return
            
        self.zero_sensor()
            
    def zero_sensor(self):
        """Reads the sensor to establish a baseline 'zero' angle."""
        try:
            # Average a few readings for a stable zero-point
            readings_w = []
            for _ in range(10):
                qw = self.sensor.quaternion[0]
                if qw is not None:
                    readings_w.append(qw)
            
            if not readings_w:
                raise RuntimeError("Failed to get a valid reading from the sensor.")

            avg_qw = sum(readings_w) / len(readings_w)
            avg_qw = max(min(avg_qw, 1.0), -1.0)
            self.initial_angle = math.acos(avg_qw) * 2 * (180 / math.pi)
            logging.info(f"Sensor zeroed. Initial angle set to: {self.initial_angle:.2f}")

            # --- Update UI for the next step ---
            self.instruction_label.config(text="Lift your leg as high as you can.")
            self.max_angle_label.pack(pady=20)
            self.max_angle_label.config(text=f"Max Angle: {self.max_angle:.1f}°")
            
            # Show the complete button
            self.complete_button.grid(row=0, column=0, ipady=10, ipadx=20)
            
            # Start tracking the angle
            self.is_tracking = True
            self.track_max_angle()

        except (OSError, RuntimeError) as e:
            logging.error(f"Could not zero sensor due to an error: {e}")
            messagebox.showerror("Sensor Error", "Could not read from the angle sensor. Please close and try again.")
            self.on_closing()

    def track_max_angle(self):
        """Continuously reads the sensor and updates the maximum angle achieved."""
        if not self.is_tracking:
            return

        try:
            if self.sensor and self.initial_angle is not None:
                qw = self.sensor.quaternion[0]
                if qw is not None:
                    qw = max(min(qw, 1.0), -1.0)
                    current_abs_angle = math.acos(qw) * 2 * (180 / math.pi)
                    relative_angle = current_abs_angle - self.initial_angle
                    
                    if relative_angle > self.max_angle:
                        self.max_angle = relative_angle
                        self.max_angle_label.config(text=f"Max Angle: {self.max_angle:.1f}°")
        except (OSError, RuntimeError) as e:
            logging.warning(f"Skipped an angle read during tracking: {e}")
        
        # Reschedule this method to run again
        self.after(50, self.track_max_angle)

    def finish_calibration(self):
        """Stops tracking, passes the zero-angle to the callback, and closes."""
        self.is_tracking = False
        logging.info(f"Calibration complete. Final Max Angle: {self.max_angle:.2f}°")
        
        self.on_complete_callback(self.initial_angle)
        self.destroy()

    def on_closing(self):
        """Handles the window being closed manually."""
        self.is_tracking = False
        logging.warning("Calibration was cancelled by the user.")
        self.destroy()