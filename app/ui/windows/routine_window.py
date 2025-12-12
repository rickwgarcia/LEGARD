import tkinter as tk
from tkinter import ttk, messagebox
import serial
import threading
import queue
import re
import csv
import time
import math
import os
from datetime import datetime
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import logging
from core.config_manager import config

# ---------------------
# File: routine_window.py
# Author: Ricardo Garcia, ricardo.garcia@cosmiac.org
# Last Modified: 2025-12-12
# Version: 2.0.0
# ---------------------

"""
Module containing the DataProcessor thread for high-frequency data analysis and
rep counting, and the RoutineWindow for real-time visualization and session management.
"""

class DataProcessor(threading.Thread):
    """
    A dedicated thread that continuously reads raw data from the shared queue
    and sensor thread, performs smoothing, calculates velocity, executes the
    rep counting algorithm, and logs all processed data to a CSV file.
    """
    def __init__(self, sensor_thread, data_queue, plot_queue, username, initial_angle=None, max_angle=None):
        """
        Initializes the DataProcessor thread.

        Args:
            sensor_thread (SensorThread): Active thread for angle data (BNO055).
            data_queue (queue.Queue): Shared queue for serial data (Wii Board/CoP).
            plot_queue (queue.Queue): Output queue to send processed data/commands to the RoutineWindow.
            username (str): Current user's username for file logging.
            initial_angle (float, optional): The zeroed baseline angle from calibration.
            max_angle (float, optional): The maximum angle from calibration (used to set target).
        """
        super().__init__(daemon=True)
        self.running = False
        self.sensor_thread = sensor_thread
        self.data_queue = data_queue
        self.plot_queue = plot_queue
        self.username = username
        self.csv_file = None
        self.csv_writer = None
        self.start_time = 0.0
        self.initial_angle_w = initial_angle
        self.cop_pattern = re.compile(r"\(([-]?\d+\.\d+), ([-]?\d+\.\d+)\)")
        self.last_known_angle = 0.0
        
        # Rep Counting State Machine variables
        self.rep_count = 0
        self.rep_state = 0 # 0: Ready, 1: Positive movement, 2: Negative movement, 3: Peak/Trough reached
        self.last_time = 0.0
        self.last_smoothed_angle = 0.0
        self.consecutive_failed_reps = 0
        self.max_angle_for_current_rep = 0.0
        self.is_first_smooth_calc = True
        self.readings_to_discard = 0
        
        # Configuration parameters loaded from config.ini
        self.SMOOTHING_WINDOW = config.getint('RepCounter', 'smoothing_window')
        self.angle_buffer = deque(maxlen=self.SMOOTHING_WINDOW)
        self.VELOCITY_SMOOTHING_WINDOW = config.getint('RepCounter', 'velocity_smoothing_window', fallback=5)
        self.velocity_buffer = deque(maxlen=self.VELOCITY_SMOOTHING_WINDOW)
        self.VELOCITY_NEG_THRESHOLD = config.getfloat('RepCounter', 'velocity_neg_threshold', fallback=-20.0)
        self.VELOCITY_POS_THRESHOLD = config.getfloat('RepCounter', 'velocity_pos_threshold', fallback=20.0)
        self.VELOCITY_ZERO_THRESHOLD = config.getfloat('RepCounter', 'velocity_zero_threshold', fallback=10.0)
        
        self.current_set = 1
        self.set_active = False
        
        self.calibrated_max_angle = max_angle if max_angle is not None else 90.0
        
        if self.calibrated_max_angle <= 0:
            self.target_angle_threshold = 9999.0
        else:
            self.MAX_ANGLE_TOLERANCE_PERCENT = config.getfloat('RepCounter', 'max_angle_tolerance_percent', fallback=90.0)
            self.target_angle_threshold = self.calibrated_max_angle * (self.MAX_ANGLE_TOLERANCE_PERCENT / 100.0)
            
        self.should_save = True
        self.log_filename = None

    def run(self):
        """The core thread loop: initializes CSV, reads raw queue, processes data, and logs."""
        self.running = True
        self.setup_csv()
        
        while self.running:
            try:
                line = self.data_queue.get(timeout=1)
                # Only process if set is active, otherwise we just drain the queue
                if self.set_active:
                    self.parse_and_process(line)
            except queue.Empty:
                continue
            except Exception:
                time.sleep(0.1)
                
        self.close_csv()

    def start_set(self):
        """Resets rep counting variables, starts the timer, and enables data processing."""
        logging.info(f"--- Starting Set {self.current_set} ---")
        self.rep_count = 0
        self.rep_state = 0
        self.start_time = time.monotonic()
        self.last_time = self.start_time
        self.consecutive_failed_reps = 0
        self.max_angle_for_current_rep = 0.0
        self.angle_buffer.clear()
        self.velocity_buffer.clear()
        self.last_known_angle = 0.0
        self.is_first_smooth_calc = True
        self.readings_to_discard = 0
        self.set_active = True
        self.plot_queue.put(f"SET_START:{self.current_set}")

    def end_set(self, reason=""):
        """Stops data processing for the current set, sends an END command to the GUI, and increments the set counter."""
        if not self.set_active: return
        logging.info(f"--- Ending Set {self.current_set} ({reason}) ---")
        self.set_active = False
        rep_count_at_stop = self.rep_count
        self.plot_queue.put(f"SET_END:{self.current_set}:{reason}:{rep_count_at_stop}")
        self.current_set += 1

    def parse_and_process(self, line):
        """
        Parses the raw serial data (CoP), fetches the angle from the SensorThread,
        performs smoothing, calculates velocity, runs the rep detection algorithm,
        sends data to the plot queue, and writes to CSV.
        """
        cop_match = self.cop_pattern.match(line)
        if not cop_match: return

        try:
            x, y = map(float, cop_match.groups())
            if not (-20 < x < 20 and -20 < y < 20): return
            
            relative_angle = self.last_known_angle
            
            # Read Angle from Sensor Thread
            if self.sensor_thread:
                qw = self.sensor_thread.get_quaternion()[0]
                if qw is not None:
                    qw = max(min(qw, 1.0), -1.0)
                    abs_angle = math.acos(qw) * 2 * (180 / math.pi)
                    
                    if self.initial_angle_w is None: self.initial_angle_w = abs_angle
                    angle_candidate = abs_angle - self.initial_angle_w
                    
                    if angle_candidate >= 0 and abs(angle_candidate - self.last_known_angle) < 180:
                        relative_angle = angle_candidate
                        self.last_known_angle = relative_angle

            # Smoothing
            self.angle_buffer.append(relative_angle)
            if len(self.angle_buffer) < self.SMOOTHING_WINDOW: return
            
            smoothed_angle = sum(self.angle_buffer) / self.SMOOTHING_WINDOW
            current_time = time.monotonic() - self.start_time 
            delta_time = current_time - self.last_time

            # Velocity Calculation
            delta_angle = 0.0
            raw_velocity = 0.0

            if self.is_first_smooth_calc:
                self.is_first_smooth_calc = False
            elif delta_time > 0:
                delta_angle = smoothed_angle - self.last_smoothed_angle
                raw_velocity = delta_angle / delta_time
            
            self.velocity_buffer.append(raw_velocity)
            smoothed_velocity = sum(self.velocity_buffer) / len(self.velocity_buffer) if self.velocity_buffer else 0.0

            self.last_time = current_time
            self.last_smoothed_angle = smoothed_angle
            is_moving = abs(smoothed_velocity) >= self.VELOCITY_ZERO_THRESHOLD
            
            # Rep Detection State Machine
            if self.set_active:
                if self.rep_state == 0: # Ready to start rep (must be still)
                    if smoothed_velocity > self.VELOCITY_POS_THRESHOLD: self.rep_state = 1
                    elif smoothed_velocity < self.VELOCITY_NEG_THRESHOLD: self.rep_state = 2
                elif self.rep_state == 1: # Moving positively (upward)
                    self.max_angle_for_current_rep = max(self.max_angle_for_current_rep, smoothed_angle)
                    if smoothed_velocity < self.VELOCITY_NEG_THRESHOLD: self.rep_state = 3 # Reached peak/reversing
                elif self.rep_state == 2: # Moving negatively (downward)
                    self.max_angle_for_current_rep = max(self.max_angle_for_current_rep, smoothed_angle)
                    if smoothed_velocity > self.VELOCITY_POS_THRESHOLD: self.rep_state = 3 # Reached trough/reversing
                elif self.rep_state == 3: # In reversal/transition, waiting to stop
                    if not is_moving:
                        # Rep completed check
                        if self.max_angle_for_current_rep < self.target_angle_threshold:
                            self.consecutive_failed_reps += 1
                        else:
                            self.consecutive_failed_reps = 0 
                        
                        self.rep_count += 1
                        self.rep_state = 0
                        self.max_angle_for_current_rep = 0.0
                        
                        if self.consecutive_failed_reps >= 3:
                            self.end_set(reason="3 failed reps")
                            return

                # Output data
                data_packet = (current_time, smoothed_angle, smoothed_velocity, x, y, self.rep_count, self.current_set)
                self.plot_queue.put(data_packet)
                
                # CSV logging
                if self.csv_writer:
                    self.csv_writer.writerow([self.current_set, f"{current_time:.4f}", self.rep_count, f"{smoothed_angle:.4f}", f"{smoothed_velocity:.4f}", f"{x:.4f}", f"{y:.4f}"])

        except (ValueError, TypeError):
            pass
            
    def setup_csv(self):
        """Creates the session directory and initializes the CSV file with metadata and headers."""
        try:
            sessions_dir = config.get('Paths', 'sessions_base_dir')
            user_session_path = os.path.join(sessions_dir, self.username)
            os.makedirs(user_session_path, exist_ok=True)
            self.log_filename = os.path.join(user_session_path, f"datalog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            self.csv_file = open(self.log_filename, 'w', newline='', encoding='utf-8')
            self.csv_writer = csv.writer(self.csv_file)
            
            # Write Max and Target Angle Metadata
            self.csv_writer.writerow(['Max', f"{self.calibrated_max_angle:.4f}"])
            
            target_val = self.target_angle_threshold if self.target_angle_threshold != 9999.0 else 0.0
            self.csv_writer.writerow(['Target', f"{target_val:.4f}"])
            
            # Data Headers
            self.csv_writer.writerow(['Set', 'Time', 'Reps', 'Angle', 'Velocity', 'X', 'Y'])
        except IOError: self.csv_file = None

    def close_csv(self):
        """Closes the CSV file, and if `should_save` is False, deletes the file."""
        if self.csv_file:
            self.csv_file.close(); self.csv_file = None
            if not self.should_save:
                try: os.remove(self.log_filename)
                except OSError: pass

    def discard_data(self): 
        """Sets the flag to delete the CSV file upon closing."""
        self.should_save = False
        
    def stop(self): 
        """Stops the thread's execution loop."""
        self.running = False

class RestTimerWindow(tk.Toplevel):
    """
    A full-screen Toplevel window that displays a countdown timer
    between exercise sets.
    """
    def __init__(self, parent, total_seconds):
        """
        Initializes the RestTimerWindow.

        Args:
            parent (tk.Toplevel): The RoutineWindow instance.
            total_seconds (int): The duration of the rest period.
        """
        super().__init__(parent)
        self.title("Rest Timer")
        self.attributes('-fullscreen', True)
        self.remaining = total_seconds
        main_frame = ttk.Frame(self, padding=50); main_frame.pack(expand=True, fill='both')
        main_frame.rowconfigure(0, weight=1); main_frame.rowconfigure(1, weight=2); main_frame.rowconfigure(2, weight=1); main_frame.columnconfigure(0, weight=1)
        style = ttk.Style(self)
        style.configure('Timer.TLabel', font=('Helvetica', 150, 'bold'), anchor='center')
        style.configure('Rest.TLabel', font=('Helvetica', 40, 'bold'), anchor='center')
        style.configure('Skip.TButton', font=('Helvetica', 20, 'bold'), padding=20)
        ttk.Label(main_frame, text="REST TIME", style='Rest.TLabel').grid(row=0, column=0, sticky='s')
        self.timer_var = tk.StringVar()
        self.timer_label = ttk.Label(main_frame, textvariable=self.timer_var, style='Timer.TLabel')
        self.timer_label.grid(row=1, column=0, sticky='nsew')
        self.skip_button = ttk.Button(main_frame, text="Skip Rest", command=self.destroy, style='Skip.TButton')
        self.skip_button.grid(row=2, column=0, sticky='n', pady=20)
        self.protocol("WM_DELETE_WINDOW", self.skip_and_close)
        self.bind('<Escape>', lambda e: self.skip_and_close())
        self.countdown_job = None
        self.update_timer()
        self.grab_set(); self.wait_window()

    def update_timer(self):
        """Decrements the timer and updates the display, scheduling the next update."""
        mins, secs = divmod(self.remaining, 60)
        self.timer_var.set(f"{mins:02d}:{secs:02d}")
        if self.remaining > 0:
            self.remaining -= 1
            self.countdown_job = self.after(1000, self.update_timer)
        else: self.destroy()

    def skip_and_close(self):
        """Cancels the countdown job and closes the window immediately."""
        if self.countdown_job: self.after_cancel(self.countdown_job)
        self.destroy()

class RoutineWindow(tk.Toplevel):
    """
    The main live session window for the exercise routine.

    It manages the UI, starts and stops sets, displays real-time plots (CoP and
    Angle) using Matplotlib's FuncAnimation, and handles inter-set breaks.
    """
    def __init__(self, parent, username, sensor, shared_queue, sensor_thread, serial_thread, initial_angle=None, max_angle=None):
        """
        Initializes the RoutineWindow.

        Args:
            parent (tk.Tk): The parent window (Dashboard).
            username (str): Current user's username.
            sensor (object): BNO055 sensor object.
            shared_queue (queue.Queue): Shared queue for serial data.
            sensor_thread (SensorThread): Active thread providing angle data.
            serial_thread (SerialThread): Active thread managing serial communication.
            initial_angle (float, optional): Zeroed angle from calibration.
            max_angle (float, optional): Max angle from calibration.
        """
        super().__init__(parent)
        self.username = username
        self.title("Live Routine Session")
        self.attributes('-fullscreen', True)
        self.bind('<Escape>', lambda e: self.on_closing())

        self.is_streaming = False
        self.sensor = sensor
        self.calibrated_max_angle = max_angle
        
        self.data_queue = shared_queue
        self.sensor_thread = sensor_thread
        self.serial_thread = serial_thread

        self.target_angle_threshold = None
        if self.calibrated_max_angle is not None and self.calibrated_max_angle > 0:
            MAX_ANGLE_TOLERANCE_PERCENT = config.getfloat('RepCounter', 'max_angle_tolerance_percent', fallback=90.0)
            self.target_angle_threshold = self.calibrated_max_angle * (MAX_ANGLE_TOLERANCE_PERCENT / 100.0)

        self.data_processor_thread = None
        self.plot_queue = queue.Queue() # Queue to receive processed data from DataProcessor
        
        self.current_set = 1
        self.total_sets = 3
        
        # Plotting configuration and data history
        self.PLOT_HISTORY_LENGTH = config.getint('Plotting', 'plot_history_length')
        self.TIME_WINDOW_SECONDS = config.getint('Plotting', 'time_window_seconds')
        
        self.x_cop_history = deque(maxlen=self.PLOT_HISTORY_LENGTH)
        self.y_cop_history = deque(maxlen=self.PLOT_HISTORY_LENGTH)
        self.time_history = deque()
        self.angle_history = deque()
        
        self.rep_count_var = tk.StringVar(value="0")
        self.current_set_var = tk.StringVar(value=f"Set: {self.current_set}")

        self.setup_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        log_level = config.get('Logging', 'level').upper()
        logging.basicConfig(level=log_level, format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')
        
        # Start Data Processor
        self.data_processor_thread = DataProcessor(
            self.sensor_thread, 
            self.data_queue, 
            self.plot_queue, 
            self.username, 
            initial_angle, 
            self.calibrated_max_angle
        )
        self.data_processor_thread.start()

    def setup_ui(self):
        """Constructs the UI, including the control panel and the Matplotlib plots."""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=4)
        main_frame.rowconfigure(0, weight=1)

        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        style = ttk.Style(self)
        style.configure('Large.TButton', font=('Helvetica', 16, 'bold'), padding=15)
        style.configure('Rep.TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('RepCount.TLabel', font=('Helvetica', 35, 'bold'))
        style.configure('Set.TLabel', font=('Helvetica', 20, 'bold'), foreground='RoyalBlue')

        self.start_stop_button = ttk.Button(control_frame, text="Start", command=self.toggle_stream, style='Large.TButton')
        self.start_stop_button.pack(fill="both", expand=True, pady=10)
        
        rep_frame = ttk.Frame(control_frame)
        rep_frame.pack(fill='both', expand=True, pady=20)

        set_label = ttk.Label(rep_frame, textvariable=self.current_set_var, style='Set.TLabel', anchor='center')
        set_label.pack(fill='x', pady=(0, 10))

        rep_label = ttk.Label(rep_frame, text="REPS", style='Rep.TLabel', anchor='center')
        rep_label.pack(fill='x')

        rep_count_label = ttk.Label(rep_frame, textvariable=self.rep_count_var, style='RepCount.TLabel', anchor='center')
        rep_count_label.pack(fill='x')

        exit_button = ttk.Button(control_frame, text="Exit", command=self.on_closing, style='Large.TButton')
        exit_button.pack(fill="both", expand=True, pady=10)

        data_frame = ttk.Frame(main_frame)
        data_frame.grid(row=0, column=1, sticky="nsew")

        # Matplotlib Setup
        self.fig, (self.ax_cop, self.ax_angle) = plt.subplots(1, 2, figsize=(9, 3), dpi=100, constrained_layout=True)
        
        cop_x_lim = config.getfloat('Plotting', 'cop_x_limit')
        cop_y_lim = config.getfloat('Plotting', 'cop_y_limit')
        angle_y_min = config.getfloat('Plotting', 'angle_y_min')
        angle_y_max = config.getfloat('Plotting', 'angle_y_max')

        # CoP Plot
        self.trail_line, = self.ax_cop.plot([], [], 'b-', alpha=0.5, lw=2)
        self.current_point_marker, = self.ax_cop.plot([], [], 'ro', markersize=8)
        self.ax_cop.set_xlim(-cop_x_lim, cop_x_lim); self.ax_cop.set_ylim(-cop_y_lim, cop_y_lim)
        self.ax_cop.set_xticklabels([]); self.ax_cop.set_yticklabels([])
        self.ax_cop.set_title("Center of Pressure"); self.ax_cop.grid(True)
        self.ax_cop.set_aspect('equal', adjustable='box')
        
        # Angle Plot
        self.angle_line, = self.ax_angle.plot([], [], 'g-')
        self.ax_angle.set_title("Relative Angle"); self.ax_angle.set_xlabel("Time (s)"); self.ax_angle.set_ylabel("Angle (degrees)")
        self.ax_angle.grid(True)
        self.ax_angle.set_xlim(0, self.TIME_WINDOW_SECONDS)
        self.ax_angle.set_ylim(angle_y_min, angle_y_max)
        
        if self.target_angle_threshold is not None:
            self.ax_angle.axhline(y=self.target_angle_threshold, color='green', linestyle='--', linewidth=1.5)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=data_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Start Matplotlib Animation Loop
        self.ani = FuncAnimation(self.fig, self.animate_plot, interval=16, blit=True, cache_frame_data=False)

    def toggle_stream(self):
        """Toggles the state of the exercise session (Start Set / Stop Set)."""
        if not self.is_streaming:
            if self.current_set > self.total_sets:
                return
            # Start the current set processing in the data thread
            self.data_processor_thread.start_set() 
            self.start_stop_button.config(text=f"Stop Set {self.current_set}")
            self.is_streaming = True
        else:
            # End the current set
            self.data_processor_thread.end_set(reason="User pressed stop")

    def disconnect(self):
        """Safely stops the DataProcessor thread and waits for it to finish."""
        if self.is_streaming and self.data_processor_thread:
             self.data_processor_thread.end_set(reason="Window closing")
        if self.data_processor_thread and self.data_processor_thread.is_alive():
            self.data_processor_thread.stop()
            self.data_processor_thread.join()

    def show_blocking_message(self, title, message):
        """Displays a modal message box."""
        messagebox.showinfo(title, message, parent=self)

    def handle_queue_command(self, command):
        """Processes commands (SET_START, SET_END) received from the DataProcessor thread."""
        if command.startswith("SET_START:"):
            self.current_set = int(command.split(":")[1])
            self.current_set_var.set(f"Set: {self.current_set}")
            self.time_history.clear(); self.angle_history.clear()
            self.x_cop_history.clear(); self.y_cop_history.clear()
            self.rep_count_var.set("0")
            
        elif command.startswith("SET_END:"):
            parts = command.split(':')
            set_num_finished = int(parts[1])
            reason = parts[2]
            reps = int(parts[3])
            
            if self.is_streaming:
                self.is_streaming = False
            
            next_set = set_num_finished + 1
            
            if next_set > self.total_sets:
                self.start_stop_button.config(text="Done", state="disabled")
                self.current_set_var.set("Complete!")
                self.after(10, lambda: self.show_blocking_message("Workout Complete!", f"All {self.total_sets} sets finished."))
            else:
                self.current_set = next_set
                self.current_set_var.set(f"Set: {self.current_set}")
                self.start_stop_button.config(text=f"Start")

                # Calculate rest time based on reps achieved
                timer_duration = 0
                if reason == "3 failed reps":
                    if reps <= 5: timer_duration = 300 
                    elif reps <= 12: timer_duration = 180 
                    elif reps <= 14: timer_duration = 90 
                
                if timer_duration > 0:
                    RestTimerWindow(self, timer_duration)
                else:
                    self.after(10, lambda n=set_num_finished, ns=next_set: self.show_blocking_message(f"Set {n} Complete!", f"Get ready for set {ns}."))
            
            self.rep_count_var.set("0")

    def animate_plot(self, frame):
        """
        The Matplotlib animation callback function, executed frequently (16ms interval).

        It drains the `plot_queue`, updates the historical data lists (deques), 
        updates the rep count display, and redraws the plots with the latest data.
        
        Args:
            frame (int): The current frame number (unused in this context).

        Returns:
            tuple: A tuple of Matplotlib Artist objects that need redrawing (for blitting).
        """
        processed_in_frame = 0
        latest_rep_count = self.rep_count_var.get()

        # Drain the plot queue to get the latest processed data
        while processed_in_frame < 20:
            try:
                data = self.plot_queue.get_nowait()
                if isinstance(data, str):
                    self.handle_queue_command(data)
                    continue
                current_time, relative_angle, velocity, x, y, rep_count, set_num = data
                self.time_history.append(current_time)
                self.angle_history.append(relative_angle)
                self.x_cop_history.append(x)
                self.y_cop_history.append(y)
                latest_rep_count = rep_count
                processed_in_frame += 1
            except queue.Empty:
                break
        
        # Update UI displays
        if self.is_streaming:
            self.rep_count_var.set(latest_rep_count)

        # Enforce time window limit on history (scrolling plot)
        if self.time_history:
            while self.time_history and (self.time_history[-1] - self.time_history[0] > self.TIME_WINDOW_SECONDS):
                self.time_history.popleft()
                self.angle_history.popleft()

        # Update CoP Plot
        self.trail_line.set_data(self.x_cop_history, self.y_cop_history)
        if self.x_cop_history:
             self.current_point_marker.set_data([self.x_cop_history[-1]], [self.y_cop_history[-1]])
        else:
             self.current_point_marker.set_data([], [])

        # Update Angle Plot
        self.angle_line.set_data(self.time_history, self.angle_history)
        
        if self.time_history:
            latest_time = self.time_history[-1]
            if latest_time > self.TIME_WINDOW_SECONDS:
                self.ax_angle.set_xlim(latest_time - self.TIME_WINDOW_SECONDS, latest_time)
            else:
                self.ax_angle.set_xlim(0, self.TIME_WINDOW_SECONDS)

        return self.trail_line, self.current_point_marker, self.angle_line # Return artists for blitting

    def on_closing(self):
        """
        Handles the window close event, prompting the user to save the session
        if data has been recorded, then safely closes the data processing thread.
        """
        # Automatically set to save (answer = True logic)
        self.disconnect()
        self.destroy()