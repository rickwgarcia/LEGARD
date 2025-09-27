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
from datetime import datetime
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import board
import adafruit_bno055
import logging

# --- Handles raw serial data input in a separate thread ---
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
            except (serial.SerialException, TypeError):
                logging.error("Serial device disconnected.")
                break
        
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        logging.info("Serial connection closed.")

    def stop(self):
        self.running = False

    def send(self, data):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.write(data.encode('utf-8'))
            logging.info(f"Sent: {data.strip()}")

# --- Processes and logs data in a separate thread ---
class DataProcessor(threading.Thread):
    def __init__(self, sensor, data_queue, plot_queue):
        super().__init__(daemon=True)
        self.running = False
        self.sensor = sensor
        self.data_queue = data_queue
        self.plot_queue = plot_queue
        self.csv_file = None
        self.csv_writer = None
        self.start_time = 0
        self.initial_angle_w = None
        self.cop_pattern = re.compile(r"\(([-]?\d+\.\d+), ([-]?\d+\.\d+)\)")
        self.last_known_angle = 0.0

    def run(self):
        self.running = True
        self.start_time = time.monotonic()
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
        if not cop_match or not self.sensor:
            return

        try:
            x, y = map(float, cop_match.groups())
            if not (-20 < x < 20 and -20 < y < 20):
                logging.warning(f"CoP outlier detected ({x:.1f}, {y:.1f}). Skipping point.")
                return
            qw = self.sensor.quaternion[0]
            if qw is None:
                logging.warning("BNO055 returned None. Skipping point.")
                return
            
            current_time = time.monotonic() - self.start_time
            qw = max(min(qw, 1.0), -1.0)
            abs_angle = math.acos(qw) * 2 * (180 / math.pi)
            if self.initial_angle_w is None:
                self.initial_angle_w = abs_angle
            relative_angle = abs_angle - self.initial_angle_w
            if relative_angle < 0 or abs(relative_angle - self.last_known_angle) > 180:
                logging.warning(f"Angle outlier detected ({relative_angle:.1f}). Skipping point.")
                return

            self.last_known_angle = relative_angle
            data_packet = (current_time, relative_angle, x, y)
            self.plot_queue.put(data_packet)
            if self.csv_writer:
                self.csv_writer.writerow([f"{v:.4f}" for v in data_packet])
        except (OSError, RuntimeError):
            logging.warning("BNO055 read error. Skipping point.")

    def setup_csv(self):
        try:
            filename = f"datalog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            self.csv_file = open(filename, 'w', newline='', encoding='utf-8')
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(['Time', 'Angle', 'X', 'Y'])
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

# --- Main UI and Animation Window using the timer-based FuncAnimation ---
class RoutineWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Live Routine Session")
        self.attributes('-fullscreen', True)
        self.bind('<Escape>', lambda e: self.on_closing())

        self.serial_thread = None
        self.data_processor_thread = None
        self.data_queue = queue.Queue()
        self.plot_queue = queue.Queue()

        self.PLOT_HISTORY_LENGTH = 100 
        self.TIME_WINDOW_SECONDS = 10
        
        self.x_cop_history = deque(maxlen=self.PLOT_HISTORY_LENGTH)
        self.y_cop_history = deque(maxlen=self.PLOT_HISTORY_LENGTH)
        self.time_history = deque()
        self.angle_history = deque()
        
        self.sensor = None
        
        self.setup_ui()
        self.init_sensor()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        port = "/dev/ttyUSB0" # Change this to your actual port if different
        logging.info(f"Attempting to connect to {port}...")
        
        self.serial_thread = SerialThread(port, 115200, self.data_queue)
        self.serial_thread.start()
        
        self.data_processor_thread = DataProcessor(self.sensor, self.data_queue, self.plot_queue)
        self.data_processor_thread.start()

    def init_sensor(self):
        try:
            i2c = board.I2C()
            self.sensor = adafruit_bno055.BNO055_I2C(i2c)
            logging.info("BNO055 sensor found!")
        except (ValueError, OSError) as e:
            logging.error(f"BNO055 sensor not found. Angle data will be unavailable. Error: {e}")
            self.sensor = None

    def setup_ui(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        ttk.Button(control_frame, text="Start", command=lambda: self.send_command('c')).pack(fill=tk.X, pady=2)

        data_frame = ttk.LabelFrame(main_frame, text="Live Data", padding="10")
        data_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        self.fig, (self.ax_cop, self.ax_angle) = plt.subplots(1, 2, figsize=(9, 4.5), dpi=100)
        
        self.trail_line, = self.ax_cop.plot([], [], 'b-', alpha=0.5, lw=2)
        self.current_point_marker, = self.ax_cop.plot([], [], 'ro', markersize=8)
        self.ax_cop.set_xlim(-1.5, 1.5); self.ax_cop.set_ylim(-1.5, 1.5)
        self.ax_cop.set_xlabel("X"); self.ax_cop.set_ylabel("Y")
        self.ax_cop.set_title("Center of Pressure"); self.ax_cop.grid(True)
        self.ax_cop.set_aspect('equal', adjustable='box')
        
        self.angle_line, = self.ax_angle.plot([], [], 'g-')
        self.ax_angle.set_title("Relative Angle"); self.ax_angle.set_xlabel("Time (s)")
        self.ax_angle.set_ylabel("Angle (degrees)"); self.ax_angle.grid(True)
        self.ax_angle.set_xlim(0, self.TIME_WINDOW_SECONDS)
        self.ax_angle.set_ylim(-10, 100)
        
        self.fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=data_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Target ~60 FPS with blitting enabled for max performance
        self.ani = FuncAnimation(self.fig, self.animate_plot, interval=16, blit=True)

    def disconnect(self):
        if self.data_processor_thread:
            self.data_processor_thread.stop()
        if self.serial_thread:
            self.serial_thread.stop()
        self.data_processor_thread = None
        self.serial_thread = None

    def animate_plot(self, frame):
        # Process a limited batch of data to keep the UI responsive
        for _ in range(20):
            try:
                current_time, relative_angle, x, y = self.plot_queue.get_nowait()
                self.time_history.append(current_time)
                self.angle_history.append(relative_angle)
                self.x_cop_history.append(x)
                self.y_cop_history.append(y)
            except queue.Empty:
                break
        
        # Trim old data for the scrolling window effect
        if self.time_history:
            while self.time_history[-1] - self.time_history[0] > self.TIME_WINDOW_SECONDS:
                self.time_history.popleft()
                self.angle_history.popleft()

        # Update plot data
        self.trail_line.set_data(self.x_cop_history, self.y_cop_history)
        if self.x_cop_history:
             self.current_point_marker.set_data([self.x_cop_history[-1]], [self.y_cop_history[-1]])
        else:
             self.current_point_marker.set_data([], [])

        self.angle_line.set_data(self.time_history, self.angle_history)
        
        # Efficiently update the x-axis for a smooth scrolling effect
        if self.time_history:
            latest_time = self.time_history[-1]
            if latest_time > self.TIME_WINDOW_SECONDS:
                self.ax_angle.set_xlim(latest_time - self.TIME_WINDOW_SECONDS, latest_time)
            else:
                self.ax_angle.set_xlim(0, self.TIME_WINDOW_SECONDS)

        # Return changed artists for blitting
        return self.trail_line, self.current_point_marker, self.angle_line

    def send_command(self, cmd):
        if self.serial_thread and self.serial_thread.is_alive():
            self.serial_thread.send(cmd)
        else:
            logging.warning("Not connected.")

    def on_closing(self):
        self.disconnect()
        self.destroy()

# --- Application entry point ---
if __name__ == '__main__':
    root = tk.Tk()
    root.title("Main Application")
    
    def open_routine_window():
        RoutineWindow(root)
        
    ttk.Button(root, text="Open Routine Window", command=open_routine_window).pack(pady=20, padx=20)
    root.mainloop()