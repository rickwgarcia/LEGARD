import tkinter as tk
from tkinter import ttk, messagebox
import math
import logging
import time

class CalibrationWindow(tk.Toplevel):
    # Constants for the progress bar's appearance and range
    BAR_MAX_ANGLE = 22  
    BAR_WIDTH = 500     
    BAR_HEIGHT = 40     

    def __init__(self, parent, sensor, shared_queue, sensor_thread, serial_thread, on_complete_callback):
        super().__init__(parent)
        self.parent = parent
        self.sensor = sensor
        
        # --- NEW LOGIC ---
        self.shared_queue = shared_queue
        self.sensor_thread = sensor_thread
        self.serial_thread = serial_thread
        # -----------------
        
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
        self.after(100, self.start_calibration)

    def start_calibration(self):
        """Checks for the sensor and then performs the zeroing process."""
        if not self.sensor:
            messagebox.showerror("Sensor Error", "BNO055 sensor not found. Cannot calibrate.")
            self.on_closing()
            return
        
        # --- NEW LOGIC: Send 'c' to Wii Board HERE ---
        if self.serial_thread:
            logging.info("Sending tare command to Wii Board...")
            self.serial_thread.send('z')
            logging.info("Sending start command to Wii Board...")
            self.serial_thread.send('c')
            # Clear old queue data
            with self.shared_queue.mutex:
                self.shared_queue.queue.clear()
        # ---------------------------------------------

        self.zero_sensor()
            
    def zero_sensor(self):
        """Reads the sensor to establish a baseline 'zero' angle."""
        try:
            readings_w = []
            for _ in range(10):
                # --- NEW LOGIC: Read from Thread ---
                if self.sensor_thread:
                    qw = self.sensor_thread.get_quaternion()[0]
                    readings_w.append(qw)
                time.sleep(0.02)
                # -----------------------------------
            
            if not readings_w:
                raise RuntimeError("Failed to get a valid reading from the sensor.")

            avg_qw = sum(readings_w) / len(readings_w)
            avg_qw = max(min(avg_qw, 1.0), -1.0)
            self.initial_angle = math.acos(avg_qw) * 2 * (180 / math.pi)
            logging.info(f"Sensor zeroed. Initial angle set to: {self.initial_angle:.2f}")

            # --- Update UI for the next step ---
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
        """Continuously reads the sensor and updates the maximum angle achieved."""
        if not self.is_tracking:
            return

        relative_angle = 0 
        try:
            if self.sensor_thread and self.initial_angle is not None:
                # --- NEW LOGIC: Read from Thread ---
                qw = self.sensor_thread.get_quaternion()[0]
                # -----------------------------------
                if qw is not None:
                    qw = max(min(qw, 1.0), -1.0)
                    current_abs_angle = math.acos(qw) * 2 * (180 / math.pi)
                    relative_angle = current_abs_angle - self.initial_angle
                    
                    if relative_angle > self.max_angle:
                        self.max_angle = relative_angle
                        # CAP at 22 for calibration visuals if desired, or just let it track
                    
                    self.max_angle_label.config(text=f"Max Angle: {self.max_angle:.1f}°")
        except Exception as e:
            pass
        
        self._update_progress_bar(relative_angle, self.max_angle)
        self.after(50, self.track_max_angle)

    def _update_progress_bar(self, current_angle, max_angle):
        self.progress_canvas.delete("all")

        fill_ratio = current_angle / self.BAR_MAX_ANGLE
        fill_width = self.BAR_WIDTH * fill_ratio
        fill_width = max(0, min(fill_width, self.BAR_WIDTH))
        
        self.progress_canvas.create_rectangle(0, 0, fill_width, self.BAR_HEIGHT, fill='mediumseagreen', outline="")

        max_ratio = max_angle / self.BAR_MAX_ANGLE
        max_x = self.BAR_WIDTH * max_ratio
        max_x = max(0, min(max_x, self.BAR_WIDTH))

        if max_x > 0:
            self.progress_canvas.create_line(max_x, 0, max_x, self.BAR_HEIGHT, fill='red', width=3)

    def finish_calibration(self):
        self.is_tracking = False
        self.on_complete_callback(self.initial_angle, self.max_angle)
        self.destroy()

    def on_closing(self):
        self.is_tracking = False
        # We do NOT stop threads here anymore.
        self.destroy()