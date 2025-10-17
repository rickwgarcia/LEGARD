import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
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
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import logging

# Import the config object
from config_manager import config

# --- SerialThread Class (No changes) ---
class SerialThread(threading.Thread):
    def __init__(self, port, baudrate, data_queue):
        super().__init__(daemon=True)
        self.port = port
        self.baudrate = baudrate
        self.data_queue = data_queue
        self.serial_connection = None
        self.running = False

    def run(self):
        try:
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=1)
            self.running = True
            logging.info(f"Successfully connected to {self.port}.")
        except serial.SerialException as e:
            logging.error(f"Failed to connect to {self.port}.\n{e}")
            return

        while self.running:
            try:
                line = self.serial_connection.readline().decode('utf-8').strip()
                if line:
                    self.data_queue.put(line)
            except (serial.SerialException, TypeError, UnicodeDecodeError):
                logging.error("Serial device disconnected or communication error.")
                break
        
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        logging.info("Serial connection closed.")

    def stop(self):
        self.running = False

    def send(self, data):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(data.encode('utf-8'))
                logging.info(f"Sent: {data.strip()}")
            except serial.SerialException:
                logging.error("Failed to send data; device may be disconnected.")

# --- DataProcessor Class (Updated with Rep Cooldown Logic) ---
# --- DataProcessor Class (Updated for Flexible Rep Counting) ---
class DataProcessor(threading.Thread):
    def __init__(self, sensor, data_queue, plot_queue, username, initial_angle=None):
        super().__init__(daemon=True)
        self.running = False
        self.sensor = sensor
        self.data_queue = data_queue
        self.plot_queue = plot_queue
        self.username = username
        self.csv_file = None
        self.csv_writer = None
        self.start_time = 0
        self.initial_angle_w = initial_angle
        self.cop_pattern = re.compile(r"\(([-]?\d+\.\d+), ([-]?\d+\.\d+)\)")
        self.last_known_angle = 0.0
        
        # --- Rep Counter Attributes ---
        self.rep_count = 0
        # <<< MODIFIED: New, more flexible state machine
        # 0: Idle, waiting for movement
        # 1: Upward motion detected, waiting for reversal (downward)
        # 2: Downward motion detected, waiting for reversal (upward)
        # 3: Reversal detected, waiting for movement to stop
        self.rep_state = 0  
        
        # --- Smoothing & Velocity Attributes ---
        self.SMOOTHING_WINDOW = config.getint('RepCounter', 'smoothing_window')
        self.angle_buffer = deque(maxlen=self.SMOOTHING_WINDOW)
        
        self.VELOCITY_SMOOTHING_WINDOW = config.getint('RepCounter', 'velocity_smoothing_window', fallback=5)
        self.velocity_buffer = deque(maxlen=self.VELOCITY_SMOOTHING_WINDOW)
        
        self.VELOCITY_NEG_THRESHOLD = config.getfloat('RepCounter', 'velocity_neg_threshold', fallback=-20.0)
        self.VELOCITY_POS_THRESHOLD = config.getfloat('RepCounter', 'velocity_pos_threshold', fallback=20.0)
        self.VELOCITY_ZERO_THRESHOLD = config.getfloat('RepCounter', 'velocity_zero_threshold', fallback=10.0)
        
        self.last_time = 0.0
        self.last_smoothed_angle = 0.0

    def run(self):
        self.running = True
        self.start_time = time.monotonic()
        self.last_time = self.start_time
        self.setup_csv()
        while self.running:
            try:
                line = self.data_queue.get(timeout=1)
                self.parse_and_process(line)
            except queue.Empty:
                continue
        self.close_csv()

    def parse_and_process(self, line):
        cop_match = self.cop_pattern.match(line)
        if not cop_match:
            return

        try:
            x, y = map(float, cop_match.groups())
            if not (-20 < x < 20 and -20 < y < 20):
                logging.warning(f"CoP outlier detected ({x:.1f}, {y:.1f}). Skipping point.")
                return
            
            relative_angle = self.last_known_angle
            if self.sensor:
                try:
                    qw = self.sensor.quaternion[0]
                    if qw is not None:
                        qw = max(min(qw, 1.0), -1.0)
                        abs_angle = math.acos(qw) * 2 * (180 / math.pi)
                        
                        if self.initial_angle_w is None:
                            self.initial_angle_w = abs_angle
                            logging.warning("Initial angle not set by calibration. Setting on first read.")

                        angle_candidate = abs_angle - self.initial_angle_w
                        
                        if angle_candidate >= 0 and abs(angle_candidate - self.last_known_angle) < 180:
                            relative_angle = angle_candidate
                            self.last_known_angle = relative_angle
                        else:
                            logging.warning(f"Angle outlier detected ({angle_candidate:.1f}). Using last known value.")
                    else:
                        logging.warning("BNO055 returned None. Using last known angle.")
                except (OSError, RuntimeError):
                    logging.warning("BNO055 read error. Using last known angle.")

            self.angle_buffer.append(relative_angle)
            if len(self.angle_buffer) < self.SMOOTHING_WINDOW:
                return
            
            smoothed_angle = sum(self.angle_buffer) / self.SMOOTHING_WINDOW
            current_time = time.monotonic() - self.start_time

            delta_time = current_time - self.last_time
            if delta_time > 0:
                delta_angle = smoothed_angle - self.last_smoothed_angle
                raw_velocity = delta_angle / delta_time
                self.velocity_buffer.append(raw_velocity)
            
            smoothed_velocity = sum(self.velocity_buffer) / len(self.velocity_buffer) if self.velocity_buffer else 0.0

            self.last_time = current_time
            self.last_smoothed_angle = smoothed_angle
            
            # <<< MODIFIED: New rep counting state machine
            if self.rep_state == 0:  # State 0: Idle, waiting for any movement
                if smoothed_velocity > self.VELOCITY_POS_THRESHOLD:
                    self.rep_state = 1 # Upward motion detected
                    logging.info("Rep state -> 1 (Upward motion detected)")
                elif smoothed_velocity < self.VELOCITY_NEG_THRESHOLD:
                    self.rep_state = 2 # Downward motion detected
                    logging.info("Rep state -> 2 (Downward motion detected)")

            elif self.rep_state == 1: # State 1: Upward motion, waiting for reversal (downward)
                if smoothed_velocity < self.VELOCITY_NEG_THRESHOLD:
                    self.rep_state = 3
                    logging.info("Rep state -> 3 (Reversal detected)")

            elif self.rep_state == 2: # State 2: Downward motion, waiting for reversal (upward)
                if smoothed_velocity > self.VELOCITY_POS_THRESHOLD:
                    self.rep_state = 3
                    logging.info("Rep state -> 3 (Reversal detected)")

            elif self.rep_state == 3: # State 3: Reversal happened, waiting for movement to stop
                if abs(smoothed_velocity) < self.VELOCITY_ZERO_THRESHOLD:
                    self.rep_count += 1
                    self.rep_state = 0
                    logging.info(f"Rep #{self.rep_count} counted! State -> 0 (Idle)")
            # --- End of state machine ---

            data_packet = (current_time, smoothed_angle, smoothed_velocity, x, y, self.rep_count)
            self.plot_queue.put(data_packet)
            
            if self.csv_writer:
                csv_row = [f"{current_time:.4f}", self.rep_count, f"{smoothed_angle:.4f}", f"{smoothed_velocity:.4f}", f"{x:.4f}", f"{y:.4f}"]
                self.csv_writer.writerow(csv_row)

        except (ValueError, TypeError):
            logging.warning(f"Could not parse data line: '{line}'")

    def setup_csv(self):
        try:
            sessions_dir = config.get('Paths', 'sessions_base_dir')
            user_session_path = os.path.join(sessions_dir, self.username)
            os.makedirs(user_session_path, exist_ok=True)
            
            filename = os.path.join(
                user_session_path, 
                f"datalog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )

            self.csv_file = open(filename, 'w', newline='', encoding='utf-8')
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(['Time', 'Reps', 'Angle', 'Velocity', 'X', 'Y'])
            logging.info(f"Logging data to {filename}")
        except IOError as e:
            logging.error(f"Error opening CSV file: {e}")
            self.csv_file = None

    def close_csv(self):
        if self.csv_file:
            logging.info(f"Closed log file: {self.csv_file.name}")
            self.csv_file.close()
            self.csv_file = None

    def stop(self):
        self.running = False

# --- Main UI and Animation Window (Updated) ---
## --- Main UI and Animation Window (Updated) ---
# --- Main UI and Animation Window (Updated to Hide Velocity Plot) ---
class RoutineWindow(tk.Toplevel):
    def __init__(self, parent, username, sensor, initial_angle=None):
        super().__init__(parent)
        self.username = username
        self.title("Live Routine Session")
        self.attributes('-fullscreen', True)
        self.bind('<Escape>', lambda e: self.on_closing())

        self.is_streaming = False
        self.sensor = sensor

        self.serial_thread = None
        self.data_processor_thread = None
        self.data_queue = queue.Queue()
        self.plot_queue = queue.Queue()
        
        self.PLOT_HISTORY_LENGTH = config.getint('Plotting', 'plot_history_length')
        self.TIME_WINDOW_SECONDS = config.getint('Plotting', 'time_window_seconds')
        
        self.x_cop_history = deque(maxlen=self.PLOT_HISTORY_LENGTH)
        self.y_cop_history = deque(maxlen=self.PLOT_HISTORY_LENGTH)
        self.time_history = deque()
        self.angle_history = deque()
        
        self.rep_count_var = tk.StringVar(value="0")

        self.setup_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        log_level = config.get('Logging', 'level').upper()
        logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
        
        port_setting = config.get('Serial', 'port')
        baudrate = config.getint('Serial', 'baudrate')

        port = port_setting if port_setting else next((p.device for p in serial.tools.list_ports.comports()), None)
        
        if not port:
            logging.error("No serial port found. Cannot start data collection.")
            return

        logging.info(f"Attempting to connect to {port} at {baudrate} baud...")
        
        self.serial_thread = SerialThread(port, baudrate, self.data_queue)
        self.serial_thread.start()
        
        self.data_processor_thread = DataProcessor(self.sensor, self.data_queue, self.plot_queue, self.username, initial_angle)
        self.data_processor_thread.start()

    def setup_ui(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=4)
        main_frame.rowconfigure(0, weight=1)

        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        style = ttk.Style(self)
        style.configure('Large.TButton', font=('Helvetica', 20, 'bold'), padding=15)
        style.configure('Rep.TLabel', font=('Helvetica', 24, 'bold'))
        style.configure('RepCount.TLabel', font=('Helvetica', 65, 'bold'))


        self.start_stop_button = ttk.Button(
            control_frame,
            text="Start",
            command=self.toggle_stream,
            style='Large.TButton'
        )
        self.start_stop_button.pack(fill="both", expand=True, pady=10)
        
        rep_frame = ttk.Frame(control_frame)
        rep_frame.pack(fill='both', expand=True, pady=20)

        rep_label = ttk.Label(rep_frame, text="REPS", style='Rep.TLabel', anchor='center')
        rep_label.pack(fill='x')

        rep_count_label = ttk.Label(rep_frame, textvariable=self.rep_count_var, style='RepCount.TLabel', anchor='center')
        rep_count_label.pack(fill='x')

        exit_button = ttk.Button(
            control_frame,
            text="Exit",
            command=self.on_closing,
            style='Large.TButton'
        )
        exit_button.pack(fill="both", expand=True, pady=10)

        data_frame = ttk.Frame(main_frame)
        data_frame.grid(row=0, column=1, sticky="nsew")

        # <<< MODIFIED: Added constrained_layout=True to automatically manage spacing
        self.fig, (self.ax_cop, self.ax_angle) = plt.subplots(
            1, 2, figsize=(9, 3), dpi=100, constrained_layout=True
        )
        
        # --- Get Plotting Limits from Config ---
        cop_x_lim = config.getfloat('Plotting', 'cop_x_limit')
        cop_y_lim = config.getfloat('Plotting', 'cop_y_limit')
        angle_y_min = config.getfloat('Plotting', 'angle_y_min')
        angle_y_max = config.getfloat('Plotting', 'angle_y_max')

        # --- CoP Plot Setup (Unchanged) ---
        self.trail_line, = self.ax_cop.plot([], [], 'b-', alpha=0.5, lw=2)
        self.current_point_marker, = self.ax_cop.plot([], [], 'ro', markersize=8)
        self.ax_cop.set_xlim(-cop_x_lim, cop_x_lim); self.ax_cop.set_ylim(-cop_y_lim, cop_y_lim)
        self.ax_cop.set_xticklabels([])
        self.ax_cop.set_yticklabels([])
        self.ax_cop.set_title("Center of Pressure"); self.ax_cop.grid(True)
        self.ax_cop.set_aspect('equal', adjustable='box')
        
        # --- Simplified Angle Plot Setup ---
        self.angle_line, = self.ax_angle.plot([], [], 'g-')
        self.ax_angle.set_title("Relative Angle")
        self.ax_angle.set_xlabel("Time (s)")
        self.ax_angle.set_ylabel("Angle (degrees)")
        self.ax_angle.grid(True)
        self.ax_angle.set_xlim(0, self.TIME_WINDOW_SECONDS)
        self.ax_angle.set_ylim(angle_y_min, angle_y_max)
        
        # <<< REMOVED: This line is no longer needed when using constrained_layout
        # self.fig.tight_layout() 
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=data_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.ani = FuncAnimation(self.fig, self.animate_plot, interval=16, blit=True, cache_frame_data=False)

    def toggle_stream(self):
        if not self.is_streaming:
            self.send_command('c')
            self.start_stop_button.config(text="Stop")
            self.is_streaming = True
            logging.info("--> Data stream STARTED.")
        else:
            self.send_command('s')
            self.start_stop_button.config(text="Start")
            self.is_streaming = False
            logging.info("--> Data stream STOPPED.")

    def disconnect(self):
        if self.data_processor_thread and self.data_processor_thread.is_alive():
            self.data_processor_thread.stop()
            self.data_processor_thread.join()
        if self.serial_thread and self.serial_thread.is_alive():
            self.serial_thread.stop()
            self.serial_thread.join()

    def animate_plot(self, frame):
        processed_in_frame = 0
        latest_rep_count = self.rep_count_var.get()

        while processed_in_frame < 20:
            try:
                # We still unpack velocity, but we won't use it for plotting
                current_time, relative_angle, velocity, x, y, rep_count = self.plot_queue.get_nowait()
                
                self.time_history.append(current_time)
                self.angle_history.append(relative_angle)
                self.x_cop_history.append(x)
                self.y_cop_history.append(y)
                
                latest_rep_count = rep_count
                processed_in_frame += 1

            except queue.Empty:
                break
        
        self.rep_count_var.set(latest_rep_count)

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

        return self.trail_line, self.current_point_marker, self.angle_line

    def send_command(self, cmd):
        if self.serial_thread and self.serial_thread.is_alive():
            self.serial_thread.send(cmd + '\n')
        else:
            logging.warning("Cannot send command: Not connected.")

    def on_closing(self):
        logging.info("Exit button clicked. Shutting down...")
        self.disconnect()
        self.destroy()