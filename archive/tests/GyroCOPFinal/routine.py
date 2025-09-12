import tkinter as tk
from tkinter import ttk, scrolledtext
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

class SerialThread(threading.Thread):
    """
    Reads raw data from the serial port and puts it into a queue.
    """
    def __init__(self, port, baudrate, data_queue, log_queue):
        super().__init__(daemon=True)
        self.port = port
        self.baudrate = baudrate
        self.data_queue = data_queue
        self.log_queue = log_queue
        self.serial_connection = None
        self.running = False

    def run(self):
        try:
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=1)
            self.running = True
            self.log_queue.put(f"Successfully connected to {self.port}.")
        except serial.SerialException as e:
            self.log_queue.put(f"Error: Failed to connect to {self.port}.\n{e}")
            return

        while self.running:
            try:
                line = self.serial_connection.readline().decode('utf-8').strip()
                if line:
                    self.data_queue.put(line)
            except (serial.SerialException, TypeError):
                self.log_queue.put("Error: Serial device disconnected.")
                break
        
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        self.log_queue.put("Serial connection closed.")

    def stop(self):
        self.running = False

    def send(self, data):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.write(data.encode('utf-8'))
            self.log_queue.put(f"Sent: {data.strip()}")

class DataProcessor(threading.Thread):
    """
    Handles parsing, sensor reading, and file writing in the background.
    This version includes data validation to reject faulty readings.
    """
    def __init__(self, sensor, data_queue, plot_queue, log_queue):
        super().__init__(daemon=True)
        self.running = False
        self.sensor = sensor
        self.data_queue = data_queue
        self.plot_queue = plot_queue
        self.log_queue = log_queue

        # CSV and data processing variables
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
        if not cop_match:
            return

        # If there's no sensor, we can't get an angle, so we skip.
        if not self.sensor:
            return

        try:
            # --- Attempt to read and validate all sensor data before processing ---
            
            # 1. Read CoP and check if it's within a valid range
            x, y = map(float, cop_match.groups())
            if not (-20 < x < 20 and -20 < y < 20):
                self.log_queue.put(f"⚠️ CoP outlier detected ({x:.1f}, {y:.1f}). Skipping point.")
                return

            # 2. Read Angle sensor
            qw = self.sensor.quaternion[0]
            if qw is None:
                self.log_queue.put("⚠️ BNO055 returned None. Skipping point.")
                return

            # --- If all reads are successful, proceed with calculations ---
            
            current_time = time.monotonic() - self.start_time
            
            qw = max(min(qw, 1.0), -1.0) # Clamp value for safety
            abs_angle = math.acos(qw) * 2 * (180 / math.pi)

            if self.initial_angle_w is None:
                self.initial_angle_w = abs_angle
            
            relative_angle = abs_angle - self.initial_angle_w

            # 3. Validate the calculated angle
            # Check for negative angles or impossibly large jumps
            if relative_angle < 0 or abs(relative_angle - self.last_known_angle) > 180:
                self.log_queue.put(f"⚠️ Angle outlier detected ({relative_angle:.1f}). Skipping point.")
                return
            
            # --- If all data is valid, update and send it ---

            self.last_known_angle = relative_angle # Update the last good value
            
            # Package, plot, and log the complete, valid data point
            data_packet = (current_time, relative_angle, x, y)
            self.plot_queue.put(data_packet)
            
            if self.csv_writer:
                self.csv_writer.writerow([f"{v:.4f}" for v in data_packet])

        except (OSError, RuntimeError):
            # On a hardware read error, log it and skip the data point entirely.
            self.log_queue.put("⚠️ BNO055 read error. Skipping point.")
            return

    def setup_csv(self):
        try:
            filename = f"datalog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            self.csv_file = open(filename, 'w', newline='', encoding='utf-8')
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(['Time', 'Angle', 'X', 'Y'])
            self.log_queue.put(f"Logging data to {filename}")
        except IOError as e:
            self.log_queue.put(f"Error opening CSV file: {e}")
            self.csv_file = None

    def close_csv(self):
        if self.csv_file:
            self.csv_file.close()
            self.log_queue.put(f"Closed log file: {self.csv_file.name}")
            self.csv_file = None

    def stop(self):
        self.running = False


class App(tk.Tk):
    """
    The main GUI application window.
    """
    def __init__(self):
        super().__init__()
        self.title("CoP and Angle Controller")
        self.geometry("1200x700")

        self.serial_thread = None
        self.data_processor_thread = None
        self.data_queue = queue.Queue()
        self.plot_queue = queue.Queue()
        self.log_queue = queue.Queue()

        self.PLOT_HISTORY_LENGTH = 100 
        self.x_cop_history = deque(maxlen=self.PLOT_HISTORY_LENGTH)
        self.y_cop_history = deque(maxlen=self.PLOT_HISTORY_LENGTH)
        self.time_history = deque(maxlen=self.PLOT_HISTORY_LENGTH)
        self.angle_history = deque(maxlen=self.PLOT_HISTORY_LENGTH)
        
        self.sensor = None
        
        self.setup_ui()
        self.init_sensor()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.process_log_queue()

    def init_sensor(self):
        try:
            i2c = board.I2C()
            self.sensor = adafruit_bno055.BNO055_I2C(i2c)
            self.log_message("✅ BNO055 sensor found!")
        except (ValueError, OSError) as e:
            self.log_message(f"❌ BNO055 sensor not found. Angle data will be unavailable. Error: {e}")
            self.sensor = None

    def setup_ui(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        left_panel = ttk.Frame(main_frame)
        left_panel.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        
        conn_frame = ttk.LabelFrame(left_panel, text="Connection", padding="10")
        conn_frame.pack(fill="x", expand=False)
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.port_var = tk.StringVar()
        self.port_menu = ttk.Combobox(conn_frame, textvariable=self.port_var, state="readonly")
        self.port_menu.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        self.refresh_ports()
        self.connect_button = ttk.Button(conn_frame, text="Connect", command=self.connect)
        self.connect_button.grid(row=0, column=2, padx=5)
        self.disconnect_button = ttk.Button(conn_frame, text="Disconnect", command=self.disconnect, state="disabled")
        self.disconnect_button.grid(row=0, column=3, padx=5)
        
        control_frame = ttk.LabelFrame(left_panel, text="Controls", padding="10")
        control_frame.pack(fill="x", expand=False, pady=5)
        ttk.Button(control_frame, text="Stream CoP & Angle", command=lambda: self.send_command('c')).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="Stop Stream", command=lambda: self.send_command('s')).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="Tare Scales", command=lambda: self.send_command('z')).pack(fill=tk.X, pady=2)

        data_frame = ttk.LabelFrame(main_frame, text="Live Data", padding="10")
        data_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        self.fig, (self.ax_cop, self.ax_angle) = plt.subplots(1, 2, figsize=(9, 4.5), dpi=100)
        
        self.trail_line, = self.ax_cop.plot([], [], 'b-', alpha=0.5)
        self.current_point_marker, = self.ax_cop.plot([], [], 'ro', markersize=8)
        self.ax_cop.set_xlim(-1.5, 1.5)
        self.ax_cop.set_ylim(-1.5, 1.5)
        self.ax_cop.set_xlabel("X")
        self.ax_cop.set_ylabel("Y")
        self.ax_cop.set_title("Center of Pressure")
        self.ax_cop.grid(True)
        self.ax_cop.set_aspect('equal', adjustable='box')
        
        self.angle_line, = self.ax_angle.plot([], [], 'g-')
        self.ax_angle.set_title("Relative Angle")
        self.ax_angle.set_xlabel("Time (s)")
        self.ax_angle.set_ylabel("Angle (degrees)")
        self.ax_angle.grid(True)
        self.ax_angle.set_ylim(-10, 90) # Adjusted Y limit to give more room

        self.fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=data_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.ani = FuncAnimation(self.fig, self.animate_plot, interval=15, blit=True)

        log_frame = ttk.LabelFrame(left_panel, text="Serial Log", padding="10")
        log_frame.pack(fill="both", expand=True, pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state="disabled", height=10)
        self.log_text.pack(fill="both", expand=True)

    def connect(self):
        port = self.port_var.get()
        if not port:
            self.log_message("Please select a port first.")
            return

        for d in [self.x_cop_history, self.y_cop_history, self.time_history, self.angle_history]:
            d.clear()
        
        self.serial_thread = SerialThread(port, 115200, self.data_queue, self.log_queue)
        self.serial_thread.start()
        
        self.data_processor_thread = DataProcessor(self.sensor, self.data_queue, self.plot_queue, self.log_queue)
        self.data_processor_thread.start()
        
        self.connect_button.config(state="disabled")
        self.disconnect_button.config(state="normal")
        self.port_menu.config(state="disabled")

    def disconnect(self):
        if self.data_processor_thread:
            self.data_processor_thread.stop()
            self.data_processor_thread = None
        if self.serial_thread:
            self.serial_thread.stop()
            self.serial_thread = None
        
        self.connect_button.config(state="normal")
        self.disconnect_button.config(state="disabled")
        self.port_menu.config(state="normal")

    def animate_plot(self, frame):
        try:
            while not self.plot_queue.empty():
                current_time, relative_angle, x, y = self.plot_queue.get_nowait()
                self.time_history.append(current_time)
                self.angle_history.append(relative_angle)
                self.x_cop_history.append(x)
                self.y_cop_history.append(y)
        except queue.Empty:
            pass
        
        self.trail_line.set_data(self.x_cop_history, self.y_cop_history)
        if self.x_cop_history:
             self.current_point_marker.set_data([self.x_cop_history[-1]], [self.y_cop_history[-1]])
        else:
             self.current_point_marker.set_data([], [])

        self.angle_line.set_data(self.time_history, self.angle_history)
        self.ax_angle.relim()
        self.ax_angle.autoscale_view(True, True, True)

        return self.trail_line, self.current_point_marker, self.angle_line

    def refresh_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_menu['values'] = ports
        if ports:
            self.port_var.set(ports[0])

    def send_command(self, cmd):
        if self.serial_thread and self.serial_thread.is_alive():
            self.serial_thread.send(cmd)
        else:
            self.log_message("Not connected.")

    def process_log_queue(self):
        try:
            while not self.log_queue.empty():
                self.log_message(self.log_queue.get_nowait())
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_log_queue)

    def log_message(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def on_closing(self):
        self.disconnect()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()