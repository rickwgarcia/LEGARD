import tkinter as tk
from tkinter import ttk, messagebox
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
# Make sure you have a 'config_manager.py' file with a 'config' object
# Example config_manager.py:
# import configparser
# config = configparser.ConfigParser()
# config.read('config.ini') # Ensure config.ini exists
from config_manager import config

# --- SerialThread Class (Unchanged) ---
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
            except (serial.SerialException, TypeError, UnicodeDecodeError) as e:
                logging.error(f"Serial communication error: {e}")
                break 
            except Exception as e:
                logging.critical(f"Unexpected SerialThread error: {e}", exc_info=True)
                time.sleep(0.1) 
        
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

# --- DataProcessor Class (MODIFIED) ---
class DataProcessor(threading.Thread):
    def __init__(self, sensor, data_queue, plot_queue, username, initial_angle=None, max_angle=None):
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
        
        # --- State variables that reset per set ---
        self.rep_count = 0
        self.rep_state = 0
        self.last_time = 0.0
        self.last_smoothed_angle = 0.0
        self.consecutive_failed_reps = 0
        self.max_angle_for_current_rep = 0.0
        self.is_first_smooth_calc = True
        self.readings_to_discard = 0
        
        self.SMOOTHING_WINDOW = config.getint('RepCounter', 'smoothing_window')
        self.angle_buffer = deque(maxlen=self.SMOOTHING_WINDOW)
        self.VELOCITY_SMOOTHING_WINDOW = config.getint('RepCounter', 'velocity_smoothing_window', fallback=5)
        self.velocity_buffer = deque(maxlen=self.VELOCITY_SMOOTHING_WINDOW)
        self.VELOCITY_NEG_THRESHOLD = config.getfloat('RepCounter', 'velocity_neg_threshold', fallback=-20.0)
        self.VELOCITY_POS_THRESHOLD = config.getfloat('RepCounter', 'velocity_pos_threshold', fallback=20.0)
        self.VELOCITY_ZERO_THRESHOLD = config.getfloat('RepCounter', 'velocity_zero_threshold', fallback=10.0)
        
        # --- Set logic variables ---
        self.current_set = 1
        self.set_active = False # Flag to control processing
        
        # --- THIS IS THE VALUE WE WILL SAVE ---
        self.calibrated_max_angle = max_angle if max_angle is not None else 90.0
        
        if self.calibrated_max_angle <= 0:
            logging.warning("Calibrated max angle is <= 0. Set failure logic will be disabled.")
            self.target_angle_threshold = 9999.0 # Effectively disable check
        else:
            self.MAX_ANGLE_TOLERANCE_PERCENT = config.getfloat('RepCounter', 'max_angle_tolerance_percent', fallback=90.0)
            self.target_angle_threshold = self.calibrated_max_angle * (self.MAX_ANGLE_TOLERANCE_PERCENT / 100.0)
            
        self.should_save = True
        self.log_filename = None

    def run(self):
        self.running = True
        self.setup_csv()
        
        while self.running:
            try:
                line = self.data_queue.get(timeout=1)
                try:
                    self.parse_and_process(line)
                except Exception as e:
                    logging.error(f"Error in parse_and_process: {e}", exc_info=True)
            except queue.Empty:
                continue
            except Exception as e:
                logging.critical(f"DataProcessor main loop error: {e}", exc_info=True)
                time.sleep(0.1)
                
        self.close_csv()

    def start_set(self):
        """Resets all set-specific counters and flags."""
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
        self.readings_to_discard = 5

        self.set_active = True
        
        self.plot_queue.put(f"SET_START:{self.current_set}")

    def end_set(self, reason=""):
        """Stops processing for the current set and increments counter."""
        if not self.set_active:
            return
            
        logging.info(f"--- Ending Set {self.current_set} ({reason}) ---")
        self.set_active = False
        
        rep_count_at_stop = self.rep_count
        self.plot_queue.put(f"SET_END:{self.current_set}:{reason}:{rep_count_at_stop}")
        
        self.current_set += 1

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

            if self.set_active and self.readings_to_discard > 0:
                self.readings_to_discard -= 1
                logging.debug(f"Discarding initial reading. {self.readings_to_discard} left.")
                return

            self.angle_buffer.append(relative_angle)
            if len(self.angle_buffer) < self.SMOOTHING_WINDOW:
                return
            
            smoothed_angle = sum(self.angle_buffer) / self.SMOOTHING_WINDOW
            current_time = time.monotonic() - self.start_time 
            delta_time = current_time - self.last_time

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
            
            if self.set_active:
                if self.rep_state == 0: # IDLE
                    if smoothed_velocity > self.VELOCITY_POS_THRESHOLD:
                        self.rep_state = 1
                    elif smoothed_velocity < self.VELOCITY_NEG_THRESHOLD:
                        self.rep_state = 2
                elif self.rep_state == 1: # UP
                    self.max_angle_for_current_rep = max(self.max_angle_for_current_rep, smoothed_angle)
                    if smoothed_velocity < self.VELOCITY_NEG_THRESHOLD:
                        self.rep_state = 3
                elif self.rep_state == 2: # DOWN
                    self.max_angle_for_current_rep = max(self.max_angle_for_current_rep, smoothed_angle)
                    if smoothed_velocity > self.VELOCITY_POS_THRESHOLD:
                        self.rep_state = 3
                elif self.rep_state == 3: # REVERSAL
                    if not is_moving:
                        if self.max_angle_for_current_rep < self.target_angle_threshold:
                            self.consecutive_failed_reps += 1
                            logging.warning(f"Failed rep #{self.consecutive_failed_reps} (Peak: {self.max_angle_for_current_rep:.1f}° < Target: {self.target_angle_threshold:.1f}°)")
                        else:
                            if self.consecutive_failed_reps > 0:
                                logging.info(f"Successful rep. Resetting failure count.")
                            self.consecutive_failed_reps = 0 
                        
                        self.rep_count += 1
                        logging.info(f"Rep #{self.rep_count} counted! State -> 0 (Idle)")
                        self.rep_state = 0
                        self.max_angle_for_current_rep = 0.0
                        
                        if self.consecutive_failed_reps >= 3:
                            logging.info(f"Set ended: 3 consecutive failed reps.")
                            self.end_set(reason="3 failed reps")
                            return

                data_packet = (current_time, smoothed_angle, smoothed_velocity, x, y, self.rep_count, self.current_set)
                self.plot_queue.put(data_packet)
                
                if self.csv_writer:
                    # This is the row that is written for every data point
                    csv_row = [
                        self.current_set, 
                        f"{current_time:.4f}", 
                        self.rep_count, 
                        f"{smoothed_angle:.4f}", 
                        f"{smoothed_velocity:.4f}", 
                        f"{x:.4f}", 
                        f"{y:.4f}"
                    ]
                    self.csv_writer.writerow(csv_row)

        except (ValueError, TypeError):
            logging.warning(f"Could not parse data line: '{line}'")
            
    # --- MODIFIED ---
    def setup_csv(self):
        try:
            sessions_dir = config.get('Paths', 'sessions_base_dir')
            user_session_path = os.path.join(sessions_dir, self.username)
            os.makedirs(user_session_path, exist_ok=True)
            self.log_filename = os.path.join(
                user_session_path, 
                f"datalog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            self.csv_file = open(self.log_filename, 'w', newline='', encoding='utf-8')
            self.csv_writer = csv.writer(self.csv_file)
            
            # --- MODIFICATION ---
            # Write the metadata row as the FIRST line in the file
            self.csv_writer.writerow(['Max', f"{self.calibrated_max_angle:.4f}"])
            
            # Write the data headers as the SECOND line
            self.csv_writer.writerow(['Set', 'Time', 'Reps', 'Angle', 'Velocity', 'X', 'Y'])
            # --- END MODIFICATION ---
            
            logging.info(f"Logging data to {self.log_filename}")
        except IOError as e:
            logging.error(f"Error opening CSV file: {e}")
            self.csv_file = None

    def close_csv(self):
        if self.csv_file:
            logging.info(f"Closing log file stream for: {self.log_filename}")
            self.csv_file.close()
            self.csv_file = None
            if self.should_save:
                logging.info(f"Session data SAVED to {self.log_filename}")
            else:
                try:
                    os.remove(self.log_filename)
                    logging.info(f"Session data DISCARDED for {self.log_filename}")
                except OSError as e:
                    logging.error(f"Error removing discarded log file {self.log_filename}: {e}")

    def discard_data(self):
        self.should_save = False
        logging.info("CSV file marked for discarding on exit.")

    def stop(self):
        self.running = False

# --- NEW CLASS: RestTimerWindow (Unchanged) ---
class RestTimerWindow(tk.Toplevel):
    def __init__(self, parent, total_seconds):
        super().__init__(parent)
        self.title("Rest Timer")
        self.attributes('-fullscreen', True)
        
        self.remaining = total_seconds
        
        # --- UI ---
        main_frame = ttk.Frame(self, padding=50)
        main_frame.pack(expand=True, fill='both')

        # Configure grid to center content
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=2) # Timer bigger
        main_frame.rowconfigure(2, weight=1) # Skip button
        main_frame.columnconfigure(0, weight=1)
        
        style = ttk.Style(self)
        style.configure('Timer.TLabel', font=('Helvetica', 150, 'bold'), anchor='center')
        style.configure('Rest.TLabel', font=('Helvetica', 40, 'bold'), anchor='center')
        style.configure('Skip.TButton', font=('Helvetica', 20, 'bold'), padding=20)

        ttk.Label(main_frame, text="REST TIME", style='Rest.TLabel').grid(row=0, column=0, sticky='s')

        self.timer_var = tk.StringVar()
        self.timer_label = ttk.Label(main_frame, textvariable=self.timer_var, style='Timer.TLabel')
        self.timer_label.grid(row=1, column=0, sticky='nsew')
        
        self.skip_button = ttk.Button(
            main_frame, 
            text="Skip Rest", 
            command=self.destroy, # 'destroy' will stop the timer
            style='Skip.TButton'
        )
        self.skip_button.grid(row=2, column=0, sticky='n', pady=20)
        
        # --- Logic ---
        self.protocol("WM_DELETE_WINDOW", self.skip_and_close) # Handle window close
        self.bind('<Escape>', lambda e: self.skip_and_close())
        
        self.countdown_job = None # To store the .after() job ID
        self.update_timer() # Start the countdown
        
        # --- Make it modal (blocks other windows) ---
        self.grab_set()
        self.wait_window()

    def update_timer(self):
        """Recursively updates the timer label every second."""
        mins, secs = divmod(self.remaining, 60)
        self.timer_var.set(f"{mins:02d}:{secs:02d}")
        
        if self.remaining > 0:
            self.remaining -= 1
            self.countdown_job = self.after(1000, self.update_timer)
        else:
            self.destroy() # Time's up

    def skip_and_close(self):
        """Ensures the .after() loop is cancelled before closing."""
        if self.countdown_job:
            self.after_cancel(self.countdown_job)
        self.destroy()

# --- RoutineWindow Class (Unchanged) ---
class RoutineWindow(tk.Toplevel):
    def __init__(self, parent, username, sensor, initial_angle=None, max_angle=None):
        super().__init__(parent)
        self.username = username
        self.title("Live Routine Session")
        self.attributes('-fullscreen', True)
        self.bind('<Escape>', lambda e: self.on_closing())

        self.is_streaming = False
        self.sensor = sensor
        self.calibrated_max_angle = max_angle

        # --- MODIFICATION: Calculate the target threshold for plotting ---
        self.target_angle_threshold = None
        if self.calibrated_max_angle is not None and self.calibrated_max_angle > 0:
            # Read the same config value used by DataProcessor
            MAX_ANGLE_TOLERANCE_PERCENT = config.getfloat('RepCounter', 'max_angle_tolerance_percent', fallback=90.0)
            self.target_angle_threshold = self.calibrated_max_angle * (MAX_ANGLE_TOLERANCE_PERCENT / 100.0)
        # --- END MODIFICATION ---

        self.serial_thread = None
        self.data_processor_thread = None
        self.data_queue = queue.Queue()
        self.plot_queue = queue.Queue()
        
        self.current_set = 1
        self.total_sets = 3
        
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
        logging.basicConfig(
            level=log_level, 
            format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
        )
        
        port_setting = config.get('Serial', 'port')
        baudrate = config.getint('Serial', 'baudrate')

        port = port_setting if port_setting else next((p.device for p in serial.tools.list_ports.comports()), None)
        
        if not port:
            logging.error("No serial port found. Cannot start data collection.")
            return

        logging.info(f"Attempting to connect to {port} at {baudrate} baud...")
        
        self.serial_thread = SerialThread(port, baudrate, self.data_queue)
        self.serial_thread.start()
        
        self.data_processor_thread = DataProcessor(
            self.sensor, 
            self.data_queue, 
            self.plot_queue, 
            self.username, 
            initial_angle, 
            self.calibrated_max_angle
        )
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
        style.configure('Large.TButton', font=('Helvetica', 16, 'bold'), padding=15)
        style.configure('Rep.TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('RepCount.TLabel', font=('Helvetica', 35, 'bold'))
        style.configure('Set.TLabel', font=('Helvetica', 20, 'bold'), foreground='RoyalBlue')

        self.start_stop_button = ttk.Button(
            control_frame,
            text="Start Set 1",
            command=self.toggle_stream,
            style='Large.TButton'
        )
        self.start_stop_button.pack(fill="both", expand=True, pady=10)
        
        rep_frame = ttk.Frame(control_frame)
        rep_frame.pack(fill='both', expand=True, pady=20)

        set_label = ttk.Label(rep_frame, textvariable=self.current_set_var, style='Set.TLabel', anchor='center')
        set_label.pack(fill='x', pady=(0, 10))

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

        self.fig, (self.ax_cop, self.ax_angle) = plt.subplots(
            1, 2, figsize=(9, 3), dpi=100, constrained_layout=True
        )
        
        cop_x_lim = config.getfloat('Plotting', 'cop_x_limit')
        cop_y_lim = config.getfloat('Plotting', 'cop_y_limit')
        angle_y_min = config.getfloat('Plotting', 'angle_y_min')
        angle_y_max = config.getfloat('Plotting', 'angle_y_max')

        self.trail_line, = self.ax_cop.plot([], [], 'b-', alpha=0.5, lw=2)
        self.current_point_marker, = self.ax_cop.plot([], [], 'ro', markersize=8)
        self.ax_cop.set_xlim(-cop_x_lim, cop_x_lim); self.ax_cop.set_ylim(-cop_y_lim, cop_y_lim)
        self.ax_cop.set_xticklabels([])
        self.ax_cop.set_yticklabels([])
        self.ax_cop.set_title("Center of Pressure"); self.ax_cop.grid(True)
        self.ax_cop.set_aspect('equal', adjustable='box')
        
        self.angle_line, = self.ax_angle.plot([], [], 'g-')
        self.ax_angle.set_title("Relative Angle")
        self.ax_angle.set_xlabel("Time (s)")
        self.ax_angle.set_ylabel("Angle (degrees)")
        self.ax_angle.grid(True)
        self.ax_angle.set_xlim(0, self.TIME_WINDOW_SECONDS)
        self.ax_angle.set_ylim(angle_y_min, angle_y_max)
        
        # --- MODIFICATION: Draw only the Target Threshold line ---
        if self.target_angle_threshold is not None:
            self.ax_angle.axhline(
                y=self.target_angle_threshold,
                color='green',
                linestyle='--', # Dashed line
                linewidth=1.5
            )
            logging.info(f"Drawing target threshold line at {self.target_angle_threshold:.2f}°")
        # --- END MODIFICATION ---
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=data_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.ani = FuncAnimation(self.fig, self.animate_plot, interval=16, blit=True, cache_frame_data=False)

    def toggle_stream(self):
        if not self.is_streaming:
            if self.current_set > self.total_sets:
                logging.warning("Workout already complete.")
                return
                
            self.send_command('c')
            self.data_processor_thread.start_set() 
            self.start_stop_button.config(text=f"Stop Set {self.current_set}")
            self.is_streaming = True
            logging.info(f"--> Set {self.current_set} stream STARTED.")
        else:
            self.send_command('s')
            self.data_processor_thread.end_set(reason="User pressed stop")
            logging.info(f"--> Set {self.current_set} stream STOPPED by user.")

    def disconnect(self):
        if self.is_streaming and self.data_processor_thread:
             self.data_processor_thread.end_set(reason="Window closing")
             
        if self.data_processor_thread and self.data_processor_thread.is_alive():
            self.data_processor_thread.stop()
            self.data_processor_thread.join()
        if self.serial_thread and self.serial_thread.is_alive():
            self.serial_thread.stop()
            self.serial_thread.join()

    def show_blocking_message(self, title, message):
        """Helper to show a messagebox outside the animation loop."""
        logging.debug(f"Showing message: '{title}'")
        messagebox.showinfo(title, message, parent=self)

    def handle_queue_command(self, command):
        """Handles string-based commands from the plot_queue."""
        logging.debug(f"GUI received command: {command}")
        
        if command.startswith("SET_START:"):
            set_num_started = int(command.split(":")[1])
            self.current_set = set_num_started
            self.current_set_var.set(f"Set: {self.current_set}")
            self.time_history.clear()
            self.angle_history.clear()
            self.x_cop_history.clear()
            self.y_cop_history.clear()
            self.rep_count_var.set("0")
            
        elif command.startswith("SET_END:"):
            try:
                parts = command.split(':')
                set_num_finished = int(parts[1])
                reason_for_end = parts[2]
                reps_completed = int(parts[3])
            except Exception as e:
                logging.error(f"Failed to parse SET_END command: {command}. Error: {e}")
                set_num_finished = int(command.split(":")[1])
                reason_for_end = "Unknown"
                reps_completed = 0
            
            if self.is_streaming:
                self.send_command('s')
                self.is_streaming = False
            
            next_set = set_num_finished + 1
            
            if next_set > self.total_sets:
                self.start_stop_button.config(text="Done", state="disabled")
                self.current_set_var.set("Complete!")
                self.after(10, lambda: self.show_blocking_message(
                    "Workout Complete!", 
                    f"Great job! All {self.total_sets} sets are finished."
                ))
            else:
                self.current_set = next_set
                self.current_set_var.set(f"Set: {self.current_set}")
                self.start_stop_button.config(text=f"Start Set {self.current_set}")

                timer_duration = 0
                if reason_for_end == "3 failed reps":
                    if 1 <= reps_completed <= 5:
                        timer_duration = 300 # 5 minutes
                    elif 6 <= reps_completed <= 12:
                        timer_duration = 180 # 3 minutes
                    elif 13 <= reps_completed <= 14:
                        timer_duration = 90 # 90 seconds
                    elif reps_completed >= 15:
                        timer_duration = 0 # No timer
                    
                    logging.info(f"Set failed. Reps: {reps_completed}. Timer: {timer_duration}s.")
                
                if timer_duration > 0:
                    RestTimerWindow(self, timer_duration)
                else:
                    self.after(10, lambda set_num=set_num_finished, ns=next_set: self.show_blocking_message(
                        f"Set {set_num} Complete!", 
                        f"Get ready for set {ns}."
                    ))
            
            self.rep_count_var.set("0") # Reset rep count for next set

    def animate_plot(self, frame):
        processed_in_frame = 0
        latest_rep_count = self.rep_count_var.get()

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
        
        if self.is_streaming:
            self.rep_count_var.set(latest_rep_count)

        if self.time_history:
            while self.time_history and (self.time_history[-1] - self.time_history[0] > self.TIME_WINDOW_SECONDS):
                self.time_history.popleft()
                self.angle_history.popleft()

        self.trail_line.set_data(self.x_cop_history, self.y_cop_history)
        if self.x_cop_history:
             self.current_point_marker.set_data([self.x_cop_history[-1]], [self.y_cop_history[-1]])
        else:
             self.current_point_marker.set_data([], [])

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
        if self.is_streaming:
            answer = messagebox.askyesnocancel(
                title="Exit Session",
                message="You are in the middle of a set.\nDo you want to save this session's data?",
                parent=self
            )
        else:
            answer = messagebox.askyesnocancel(
                title="Exit Session",
                message="Do you want to save this session's data?",
                parent=self
            )

        if answer is True:
            logging.info("User chose to SAVE. Shutting down...")
            self.disconnect()
            self.destroy()
        elif answer is False:
            logging.info("User chose to DISCARD. Shutting down...")
            if self.data_processor_thread:
                self.data_processor_thread.discard_data()
            self.disconnect()
            self.destroy()
        else:
            logging.info("User cancelled the exit operation. Returning to session.")
            pass

# --- Main execution ---
# This part is for testing. You would typically import and
# call RoutineWindow from your main application's GUI.
if __name__ == "__main__":
    # --- Create a dummy config for testing ---
    import configparser
    
    # Check if config_manager.py exists, if not, create a dummy
    try:
        from config_manager import config
    except ImportError:
        print("Creating dummy config_manager.py and config.ini")
        
        with open("config_manager.py", "w") as f:
            f.write("import configparser\n")
            f.write("config = configparser.ConfigParser()\n")
            f.write("config.read('config.ini')\n")
        
        with open("config.ini", "w") as f:
            f.write("[RepCounter]\n")
            f.write("smoothing_window = 10\n")
            f.write("velocity_smoothing_window = 5\n")
            f.write("velocity_neg_threshold = -20.0\n")
            f.write("velocity_pos_threshold = 20.0\n")
            f.write("velocity_zero_threshold = 10.0\n")
            f.write("max_angle_tolerance_percent = 90.0\n")
            f.write("[Paths]\n")
            f.write("sessions_base_dir = ./sessions\n")
            f.write("[Logging]\n")
            f.write("level = INFO\n")
            f.write("[Serial]\n")
            f.write("port = \n")
            f.write("baudrate = 115200\n")
            f.write("[Plotting]\n")
            f.write("plot_history_length = 100\n")
            f.write("time_window_seconds = 10\n")
            f.write("cop_x_limit = 10\n")
            f.write("cop_y_limit = 10\n")
            f.write("angle_y_min = -10\n")
            f.write("angle_y_max = 100\n")

        from config_manager import config
        config.read('config.ini')

    # --- Create a dummy BNO055 sensor for testing ---
    # This avoids the need for adafruit_bno055
    class DummySensor:
        @property
        def quaternion(self):
            # Simulate some noisy data
            noise = (time.time() % 2) * 0.01 - 0.005
            # Simulate a 1-second sine wave
            sim_angle = 45 * math.sin(time.time() * math.pi * 2) + 45
            # Convert angle to quaternion W component
            rad = math.radians(sim_angle / 2)
            return [math.cos(rad) + noise, 0, 0, 0]

    # --- Start the app ---
    root = tk.Tk()
    root.withdraw() # Hide the root window
    
    # Create a dummy sensor object
    # If you have the real sensor, initialize it here
    dummy_sensor = DummySensor()
    # In a real app, you would pass the actual BNO055 sensor object
    
    # --- Parameters to pass to RoutineWindow ---
    # These would come from your login and calibration windows
    TEST_USERNAME = "test_user"
    TEST_INITIAL_ANGLE = 175.0 # Dummy initial angle (absolute)
    TEST_MAX_ANGLE = 85.0     # Dummy calibrated max angle (relative)
    
    try:
        app = RoutineWindow(
            parent=root, 
            username=TEST_USERNAME, 
            sensor=dummy_sensor, 
            initial_angle=TEST_INITIAL_ANGLE, 
            max_angle=TEST_MAX_ANGLE
        )
        root.mainloop()
    except Exception as e:
        logging.critical(f"Failed to start application: {e}", exc_info=True)
        root.destroy()