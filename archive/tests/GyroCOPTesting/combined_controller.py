import tkinter as tk
from tkinter import ttk, scrolledtext
import serial
import serial.tools.list_ports
import threading  # <--- ADD THIS LINE
import queue
import re
import csv
import time
import math
from datetime import datetime
from collections import deque

# --- New Imports for Matplotlib, BNO055 Sensor, and CSV Logging ---
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import board
import adafruit_bno055


class SerialThread(threading.Thread):
    """
    A separate thread to handle reading from the serial port non-blockingly.
    (This class is unchanged from your original script)
    """
    def __init__(self, port, baudrate, data_queue, log_queue):
        super().__init__(daemon=True)
        self.port = port
        self.baudrate = baudrate
        self.data_queue = data_queue
        self.log_queue = log_queue
        self.serial_connection = None
        self.running = False
        self._calibration_weight = None
        self._is_calibrating = False

    def run(self):
        """Main loop for the thread."""
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
                    if "Enter the weight in lbs:" in line and self._is_calibrating:
                        self.send(f"{self._calibration_weight}\n")
                        self.log_queue.put(f"Sent calibration weight: {self._calibration_weight}")
                        self._is_calibrating = False 

                    self.data_queue.put(line)

            except serial.SerialException:
                self.log_queue.put("Error: Serial device disconnected.")
                break
            except Exception as e:
                self.log_queue.put(f"An error occurred in serial thread: {e}")
                
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        self.log_queue.put("Serial connection closed.")

    def stop(self):
        """Stops the thread."""
        self.running = False

    def send(self, data):
        """Sends data to the serial port."""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.write(data.encode('utf-8'))
            self.log_queue.put(f"Sent: {data.strip()}")

    def start_calibration(self, weight):
        """Initiates the calibration sequence."""
        self._calibration_weight = weight
        self._is_calibrating = True
        self.send('k')


class App(tk.Tk):
    """
    The main GUI application window, now with dual plots and data logging.
    """
    def __init__(self):
        super().__init__()
        self.title("CoP and Angle Controller")
        self.geometry("1200x700")

        # --- Data management ---
        self.serial_thread = None
        self.data_queue = queue.Queue()
        self.log_queue = queue.Queue()

        # Regex patterns
        self.cop_pattern = re.compile(r"\(([-]?\d+\.\d+), ([-]?\d+\.\d+)\)")
        self.weight_pattern = re.compile(r"([-]?\d+\.\d+),([-]?\d+\.\d+),([-]?\d+\.\d+),([-]?\d+\.\d+)")
        
        # --- Data storage for plots ---
        self.PLOT_HISTORY_LENGTH = 100 
        self.x_cop_history = deque(maxlen=self.PLOT_HISTORY_LENGTH)
        self.y_cop_history = deque(maxlen=self.PLOT_HISTORY_LENGTH)
        self.time_history = deque(maxlen=self.PLOT_HISTORY_LENGTH)
        self.angle_history = deque(maxlen=self.PLOT_HISTORY_LENGTH)
        
        # BNO055 Sensor variables
        self.sensor = None
        self.initial_angle_w = None
        self.start_time = 0

        # CSV Logging Setup
        self.csv_file = None
        self.csv_writer = None

        # --- CORRECTED ORDER ---
        # 1. Create the UI widgets first!
        self.setup_ui()
        
        # 2. Now it's safe to initialize the sensor and log messages
        self.init_sensor()

        # 3. Set up remaining app behavior
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.process_log_queue()
    
    def init_sensor(self):
        """Initializes the BNO055 sensor."""
        try:
            i2c = board.I2C()
            self.sensor = adafruit_bno055.BNO055_I2C(i2c)
            self.log_message("✅ BNO055 sensor found!")
        except (ValueError, OSError) as e:
            self.log_message(f"❌ BNO055 sensor not found. Angle data will be unavailable. Error: {e}")
            self.sensor = None # Ensure sensor is None if not found

    def setup_ui(self):
        """Creates and arranges all the widgets in the window."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # --- Connection, Control, and Calibration Frames (mostly unchanged) ---
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
        ttk.Button(control_frame, text="Stream Weights", command=lambda: self.send_command('r')).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="Stream CoP & Angle", command=lambda: self.send_command('c')).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="Stop Stream", command=lambda: self.send_command('s')).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="Tare Scales", command=lambda: self.send_command('z')).pack(fill=tk.X, pady=2)

        cal_frame = ttk.LabelFrame(left_panel, text="Quick Calibration", padding="10")
        cal_frame.pack(fill="x", expand=False, pady=5)
        ttk.Label(cal_frame, text="Enter known weight (lbs):").pack(padx=5, pady=2, anchor=tk.W)
        self.cal_weight_var = tk.StringVar(value="10.0")
        ttk.Entry(cal_frame, textvariable=self.cal_weight_var).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(cal_frame, text="Calibrate", command=self.start_calibration).pack(fill=tk.X, pady=5)
        
        # --- Data Display Frame ---
        data_frame = ttk.LabelFrame(main_frame, text="Live Data", padding="10")
        data_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1) # Allow data frame to expand
        main_frame.rowconfigure(0, weight=1)   # Allow data frame to expand

        # --- NEW: Matplotlib Plots (Side-by-Side) ---
        # Create a figure that contains two subplots
        self.fig, (self.ax_cop, self.ax_angle) = plt.subplots(1, 2, figsize=(9, 4.5), dpi=100)

        # --- CoP Plot (Left) ---
        self.trail_line, = self.ax_cop.plot([], [], 'b-', alpha=0.5, label='History Trail')
        self.current_point_marker, = self.ax_cop.plot([], [], 'ro', markersize=8, label='Current Position')
        self.ax_cop.set_xlim(-1.5, 1.5)
        self.ax_cop.set_ylim(-1.5, 1.5)
        self.ax_cop.set_xlabel("X")
        self.ax_cop.set_ylabel("Y")
        self.ax_cop.set_title("Center of Pressure")
        self.ax_cop.grid(True)
        self.ax_cop.set_aspect('equal', adjustable='box')
        
        # --- NEW: Angle Plot (Right) ---
        self.angle_line, = self.ax_angle.plot([], [], 'g-', label='Relative Angle')
        self.ax_angle.set_title("Relative Angle")
        self.ax_angle.set_xlabel("Time (s)")
        self.ax_angle.set_ylabel("Angle (degrees)")
        self.ax_angle.grid(True)
        self.ax_angle.set_ylim(-90, 90) # Set a default view

        self.fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=data_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.ani = FuncAnimation(self.fig, self.animate_plot, interval=30, blit=True, save_count=10)

        # --- Log Console ---
        log_frame = ttk.LabelFrame(left_panel, text="Serial Log", padding="10")
        log_frame.pack(fill="both", expand=True, pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state="disabled", height=10)
        self.log_text.pack(fill="both", expand=True)

    def refresh_ports(self):
        """Updates the list of available serial ports."""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_menu['values'] = ports
        if ports:
            self.port_var.set(ports[0])

    def connect(self):
        """Starts the serial thread and connects to the selected port."""
        port = self.port_var.get()
        if not port:
            self.log_message("Please select a port first.")
            return

        # Baud rate is 115200 to match the Arduino code
        self.serial_thread = SerialThread(port, 115200, self.data_queue, self.log_queue)
        self.serial_thread.start()
        
        self.connect_button.config(state="disabled")
        self.disconnect_button.config(state="normal")
        self.port_menu.config(state="disabled")
        
        ### NEW: Start CSV Logging ###
        try:
            filename = f"datalog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            self.csv_file = open(filename, 'w', newline='', encoding='utf-8')
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(['Time', 'Angle', 'X', 'Y'])
            self.log_message(f"Logging data to {filename}")
        except IOError as e:
            self.log_message(f"Error opening CSV file: {e}")
            self.csv_file = None
            self.csv_writer = None

        # Reset data history and time
        for d in [self.x_cop_history, self.y_cop_history, self.time_history, self.angle_history]:
            d.clear()
        self.initial_angle_w = None
        self.start_time = time.monotonic()


    def disconnect(self):
        """Stops the serial thread."""
        if self.serial_thread and self.serial_thread.is_alive():
            self.serial_thread.stop()
        
        self.connect_button.config(state="normal")
        self.disconnect_button.config(state="disabled")
        self.port_menu.config(state="normal")

        ### NEW: Stop CSV Logging ###
        if self.csv_file:
            self.csv_file.close()
            self.log_message(f"Closed log file: {self.csv_file.name}")
            self.csv_file = None
            self.csv_writer = None

    def send_command(self, cmd):
        """Sends a single character command to the Arduino."""
        if self.serial_thread and self.serial_thread.is_alive():
            self.serial_thread.send(cmd)
        else:
            self.log_message("Not connected.")

    def start_calibration(self):
        """Handles the calibration button click."""
        if not (self.serial_thread and self.serial_thread.is_alive()):
            self.log_message("Not connected.")
            return
        
        try:
            weight = float(self.cal_weight_var.get())
            self.serial_thread.start_calibration(weight)
        except ValueError:
            self.log_message("Error: Invalid calibration weight. Please enter a number.")

    def animate_plot(self, frame):
        """This function is called periodically by FuncAnimation to update the plots."""
        try:
            # Process all pending items in the queue
            while not self.data_queue.empty():
                line = self.data_queue.get_nowait()
                self.parse_and_update(line)
        except queue.Empty:
            pass # No new data, just redraw
        
        # Update plot data for CoP
        self.trail_line.set_data(self.x_cop_history, self.y_cop_history)
        if self.x_cop_history:
             self.current_point_marker.set_data([self.x_cop_history[-1]], [self.y_cop_history[-1]])
        else:
             self.current_point_marker.set_data([], [])

        # --- NEW: Update plot data for Angle ---
        self.angle_line.set_data(self.time_history, self.angle_history)
        # Rescale view to keep the data visible
        self.ax_angle.relim()
        self.ax_angle.autoscale_view(True, True, True)

        # Return all the artists that were changed. This is required for blit=True.
        return self.trail_line, self.current_point_marker, self.angle_line
            
    def process_log_queue(self):
        """Periodically checks the log queue and updates the GUI."""
        try:
            while not self.log_queue.empty():
                self.log_message(self.log_queue.get_nowait())
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_log_queue)

    def parse_and_update(self, line):
        """Parses a line of data, reads the angle, logs to CSV, and updates data for plots."""
        # Check for CoP data first, as it's the primary trigger
        cop_match = self.cop_pattern.match(line)
        if cop_match:
            x, y = map(float, cop_match.groups())
            
            # --- NEW: Read Angle and Timestamp on CoP trigger ---
            current_time = time.monotonic() - self.start_time
            relative_angle = 0.0 # Default value if sensor fails
            
            if self.sensor:
                try:
                    # Calculate angle from quaternion
                    qw = self.sensor.quaternion[0]
                    if qw is not None:
                        if qw > 1.0: qw = 1.0
                        if qw < -1.0: qw = -1.0
                        
                        current_absolute_angle = math.acos(qw) * 2 * (180 / math.pi)

                        if self.initial_angle_w is None: # First reading, set the offset
                            self.initial_angle_w = current_absolute_angle
                        
                        relative_angle = current_absolute_angle - self.initial_angle_w
                except (OSError, RuntimeError):
                    # Keep the last known angle if there's a read error
                    if self.angle_history:
                        relative_angle = self.angle_history[-1]
            
            # Append new synchronized data to history
            self.x_cop_history.append(x)
            self.y_cop_history.append(y)
            self.time_history.append(current_time)
            self.angle_history.append(relative_angle)

            # --- NEW: Write data to CSV file ---
            if self.csv_writer:
                self.csv_writer.writerow([f"{current_time:.4f}", f"{relative_angle:.4f}", f"{x:.4f}", f"{y:.4f}"])
            
            return

        # Check for weight data (less frequent, so check second)
        weight_match = self.weight_pattern.match(line)
        if weight_match:
            # We don't have weight labels in this new layout, but you could add them back if needed
            # For now, we just log the raw line.
            self.log_message(f"Weights: {line}")
            return
            
        # Log any other lines that don't match
        self.log_message(f"Raw: {line}")


    def log_message(self, msg):
        """Appends a message to the log text area."""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END) # Auto-scroll
        self.log_text.config(state="disabled")

    def on_closing(self):
        """Handles window closing event."""
        self.disconnect()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()