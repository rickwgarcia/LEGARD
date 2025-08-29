import csv
import hashlib
import os
import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
from datetime import datetime
from collections import defaultdict
import random
import serial  # For serial communication
import serial.tools.list_ports # To help find ports
import threading
import queue
import re

# --- Matplotlib Imports for the Analytics & Settings Chart ---
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Constants ---
USER_DATA_FILE = '/home/rickg/Desktop/LEGARD/app/users/users.csv'
SESSION_DATA_FOLDER = '/home/rickg/Desktop/LEGARD/app/session_data'

# --- Serial Port Configuration (Default) ---
BAUD_RATE = 9600

# --- NEW: Thread for Non-Blocking Serial Communication ---
class SerialThread(threading.Thread):
    """
    A separate thread to handle reading from the serial port non-blockingly.
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
                    # Check if the line contains calibration prompt
                    if "Enter the weight in lbs:" in line and self._is_calibrating:
                        self.send(f"{self._calibration_weight}\n")
                        self.log_queue.put(f"Sent calibration weight: {self._calibration_weight}")
                        self._is_calibrating = False # Reset calibration state

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

# --- Backend Logic ---

def hash_pin(pin):
    """Hashes the PIN using SHA-256 for secure storage."""
    salt = "your_secret_salt" 
    salted_pin = pin + salt
    return hashlib.sha256(salted_pin.encode()).hexdigest()

def register_user(username, pin, first_name, last_name, gender):
    """Registers a new user with profile details and a PIN to users.csv."""
    if not all([username, pin, first_name, last_name, gender]):
        return (False, "All fields are required.")
    
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0] == username:
                    return (False, "Username already exists.")
                    
    hashed_pin = hash_pin(pin)
    with open(USER_DATA_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, hashed_pin, first_name, last_name, gender])
        
    return (True, f"Account for '{username}' created successfully!")

def login_user(username, pin):
    """
    Logs in a user by checking credentials against users.csv.
    Returns success status, a message, full name, and gender on success.
    """
    if not username or not pin: 
        return (False, "Username and PIN cannot be empty.", None, None)
        
    hashed_pin = hash_pin(pin)
    if not os.path.exists(USER_DATA_FILE): 
        return (False, "No user accounts found.", None, None)
        
    with open(USER_DATA_FILE, 'r', newline='') as file:
        reader = csv.reader(file)
        # Skip header if it exists
        try:
            # Check if the first row is the header
            first_row = next(reader)
            if first_row != ['username', 'hashed_pin', 'first_name', 'last_name', 'gender']:
                # If not header, check this row for login
                if first_row and first_row[0] == username and first_row[1] == hashed_pin:
                    full_name = f"{first_row[2]} {first_row[3]}"
                    gender = first_row[4]
                    return (True, f"Welcome back, {full_name}!", full_name, gender)
        except StopIteration:
            return (False, "No user accounts found.", None, None)

        # Check remaining rows
        for row in reader:
            if row and row[0] == username and row[1] == hashed_pin:
                full_name = f"{row[2]} {row[3]}"
                gender = row[4]
                return (True, f"Welcome back, {full_name}!", full_name, gender)
                
    return (False, "Invalid username or PIN.", None, None)


def save_session_to_csv(username, exercise_name, session_readings):
    """Saves a workout session's data in a time-series format to a unique CSV."""
    os.makedirs(SESSION_DATA_FOLDER, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SESSION_DATA_FOLDER}/{username}_{exercise_name}_{timestamp}.csv"
    
    header = ['Time', 'Rep', 'Angle', 'X', 'Y']
    
    try:
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(session_readings)
        return True, "Session saved successfully."
    except IOError as e:
        return False, f"Error saving file: {e}"

def count_reps_in_file(filepath):
    """Helper function to count the number of unique reps in a session file."""
    try:
        with open(filepath, 'r') as file:
            reader = csv.DictReader(file)
            reps = {int(row['Rep']) for row in reader if row.get('Rep') and row['Rep'].isdigit()}
            return len(reps) if reps else 0
    except (IOError, KeyError, ValueError):
        return 0

def get_user_sessions_from_csvs(username):
    """Scans the data folder and lists all sessions for a given user."""
    if not os.path.exists(SESSION_DATA_FOLDER): 
        return []
        
    user_sessions = []
    for filename in os.listdir(SESSION_DATA_FOLDER):
        if filename.startswith(f"{username}_") and filename.endswith(".csv"):
            parts = filename.replace('.csv', '').split('_')
            if len(parts) >= 3:
                exercise, date = parts[1], parts[2]
                
                filepath = os.path.join(SESSION_DATA_FOLDER, filename)
                rep_count = count_reps_in_file(filepath)
                
                user_sessions.append(f"{date} - {exercise} - {rep_count} reps")
            
    user_sessions.sort(reverse=True) # Show newest first
    return user_sessions

def get_reps_per_day(username):
    """Parses all session files for a user and aggregates total reps by date."""
    if not os.path.exists(SESSION_DATA_FOLDER): 
        return {}
        
    reps_by_day = defaultdict(int)
    for filename in os.listdir(SESSION_DATA_FOLDER):
        if filename.startswith(f"{username}_") and filename.endswith(".csv"):
            parts = filename.replace('.csv', '').split('_')
            if len(parts) >= 3:
                date_str = parts[2]
                filepath = os.path.join(SESSION_DATA_FOLDER, filename)
                reps_by_day[date_str] += count_reps_in_file(filepath)
            
    return dict(sorted(reps_by_day.items()))

# --- GUI Classes ---

class RegistrationWindow(tk.Toplevel):
    """A separate pop-up window for user registration with a PIN."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Register New User")
        self.geometry("350x250")

        frame = ttk.Frame(self, padding="10")
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="First Name:").grid(row=0, column=0, sticky="w", pady=2)
        self.first_name_entry = ttk.Entry(frame)
        self.first_name_entry.grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Label(frame, text="Last Name:").grid(row=1, column=0, sticky="w", pady=2)
        self.last_name_entry = ttk.Entry(frame)
        self.last_name_entry.grid(row=1, column=1, sticky="ew", pady=2)
        ttk.Label(frame, text="Gender:").grid(row=2, column=0, sticky="w", pady=2)
        self.gender_combobox = ttk.Combobox(frame, values=["Male", "Female", "Other", "Prefer not to say"])
        self.gender_combobox.grid(row=2, column=1, sticky="ew", pady=2)
        ttk.Label(frame, text="Username:").grid(row=3, column=0, sticky="w", pady=2)
        self.username_entry = ttk.Entry(frame)
        self.username_entry.grid(row=3, column=1, sticky="ew", pady=2)

        ttk.Label(frame, text="Create 4-Digit PIN:").grid(row=4, column=0, sticky="w", pady=2)
        vcmd = (self.register(self.validate_pin), '%P')
        self.pin_entry = ttk.Entry(frame, show="*", validate="key", validatecommand=vcmd)
        self.pin_entry.grid(row=4, column=1, sticky="ew", pady=2)

        submit_button = ttk.Button(frame, text="Submit Registration", command=self.submit)
        submit_button.grid(row=5, column=0, columnspan=2, pady=20)
        frame.columnconfigure(1, weight=1)

    def validate_pin(self, new_value):
        """Ensures the PIN is numeric and no more than 4 digits."""
        return (new_value == "" or new_value.isdigit()) and len(new_value) <= 4

    def submit(self):
        pin = self.pin_entry.get()
        if len(pin) != 4:
            messagebox.showerror("Error", "Your PIN must be exactly 4 digits.")
            return

        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        gender = self.gender_combobox.get()
        username = self.username_entry.get()
        success, message = register_user(username, pin, first_name, last_name, gender)
        if success:
            messagebox.showinfo("Success", message)
            self.destroy()
        else:
            messagebox.showerror("Error", message)

# --- MODIFIED: Blank Recording Session Window ---
class RecordingSessionWindow(tk.Toplevel):
    """A dedicated, blank window for you to implement the session logic."""
    def __init__(self, parent, username, serial_thread):
        super().__init__(parent)
        self.parent = parent
        self.username = username
        self.serial_thread = serial_thread

        self.title("Live Workout Session")
        self.geometry("600x400") # Made it a bit bigger for your content

        # --- This window is intentionally left blank. ---
        # --- Add your session recording widgets and logic here. ---
        
        # Example: You could add a label to get started
        ttk.Label(self, text="Implement your session recording UI here.", font=("Helvetica", 14)).pack(pady=50)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Handles the window closing event."""
        self.parent.session_window = None # Inform the parent window that this one is closed
        self.destroy()

class Dashboard(tk.Tk):
    """The main application dashboard with five tabs."""
    def __init__(self, username, full_name, gender):
        super().__init__()
        self.username = username
        self.full_name = full_name
        self.gender = gender
        self.title(f"Exercise Dashboard - Welcome {self.full_name}")
        self.geometry("850x650")

        self.session_window = None # To hold a reference to the recording window

        # --- New Serial Communication System State ---
        self.serial_thread = None
        self.data_queue = queue.Queue()
        self.log_queue = queue.Queue()
        self.cop_pattern = re.compile(r"\(([-]?\d+\.\d+), ([-]?\d+\.\d+)\)")
        self.weight_pattern = re.compile(r"([-]?\d+\.\d+),([-]?\d+\.\d+),([-]?\d+\.\d+),([-]?\d+\.\d+)")
        self.x_com_history = []
        self.y_com_history = []
        self.PLOT_HISTORY_LENGTH = 100

        # --- UI Setup ---
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")
        
        tabs = {"👤 Profile": self.create_profile_tab, "🏋️ Routine": self.create_routine_tab, "📜 History": self.create_history_tab, "📊 Analytics": self.create_analytics_tab, "⚙️ Settings": self.create_settings_tab}
        for name, creation_func in tabs.items():
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=name)
            creation_func(frame)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.process_queues() # Start the master queue processing loop

    def on_closing(self):
        """Called when the user closes the window."""
        self.disconnect() # Gracefully stop the serial thread
        if self.session_window:
            self.session_window.destroy() # Close the session window if it's open
        self.destroy()

    # --- Profile Tab ---
    def create_profile_tab(self, parent_frame):
        ttk.Label(parent_frame, text=f"Welcome, {self.full_name}!", font=("Helvetica", 16)).pack(pady=20)
        info_frame = ttk.Frame(parent_frame)
        info_frame.pack()
        ttk.Label(info_frame, text="Username:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(info_frame, text=self.username).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        ttk.Label(info_frame, text="Gender:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(info_frame, text=self.gender).grid(row=1, column=1, sticky="w", padx=5, pady=2)

    # --- Routine Tab ---
    def create_routine_tab(self, parent_frame):
        frame = ttk.Frame(parent_frame, padding="10")
        frame.pack(fill="both", expand=True, anchor="center")
        
        inner_frame = ttk.Frame(frame)
        inner_frame.pack(expand=True)

        ttk.Label(inner_frame, text="Record New Workout Session", font=("Helvetica", 16)).pack(pady=10)
        
        self.routine_status_label = ttk.Label(inner_frame, text="Disconnected. Connect in Settings tab.", foreground="red", font=("Helvetica", 10))
        self.routine_status_label.pack(pady=5)
        
        self.start_session_button = ttk.Button(inner_frame, text="Start New Session", command=self.open_session_window, state="disabled")
        self.start_session_button.pack(pady=20, ipady=10, ipadx=10)

    def open_session_window(self):
        """Checks connection and opens the dedicated recording window."""
        if not (self.serial_thread and self.serial_thread.is_alive()):
            messagebox.showerror("Error", "Device is not connected. Please connect in the Settings tab.")
            return
        
        if self.session_window:
            self.session_window.lift() 
            return
            
        self.session_window = RecordingSessionWindow(self, self.username, self.serial_thread)

    # --- History Tab ---
    def create_history_tab(self, parent_frame):
        self.history_frame = ttk.Frame(parent_frame, padding="10")
        self.history_frame.pack(fill="both", expand=True)
        ttk.Label(self.history_frame, text="Your Past Sessions", font=("Helvetica", 16)).pack(pady=10)
        self.sessions_listbox = tk.Listbox(self.history_frame)
        self.sessions_listbox.pack(fill="both", expand=True)
        self.refresh_history_tab()
    
    def refresh_history_tab(self):
        if hasattr(self, 'sessions_listbox'):
            self.sessions_listbox.delete(0, tk.END)
            sessions = get_user_sessions_from_csvs(self.username)
            for session_info in sessions:
                self.sessions_listbox.insert(tk.END, session_info)

    # --- Analytics Tab ---
    def create_analytics_tab(self, parent_frame):
        self.analytics_frame = ttk.Frame(parent_frame, padding="10")
        self.analytics_frame.pack(fill="both", expand=True)
        ttk.Label(self.analytics_frame, text="Your Performance Analytics", font=("Helvetica", 16)).pack(pady=10)
        self.chart_frame = ttk.Frame(self.analytics_frame)
        self.chart_frame.pack(fill="both", expand=True, pady=5)
        self.chart_label = ttk.Label(self.chart_frame, text="Click the button to generate your reps-per-day chart.")
        self.chart_label.pack(pady=20)
        generate_button = ttk.Button(self.analytics_frame, text="Generate/Refresh Chart", command=self.display_reps_chart)
        generate_button.pack(pady=10)

    def display_reps_chart(self):
        for widget in self.chart_frame.winfo_children(): widget.destroy()
        reps_data = get_reps_per_day(self.username)
        if not reps_data:
            ttk.Label(self.chart_frame, text="No data available to generate a chart.").pack(pady=20)
            return
        dates, reps = list(reps_data.keys()), list(reps_data.values())
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(dates, reps, color='skyblue')
        ax.set_title("Total Reps Per Day")
        ax.set_ylabel("Number of Reps")
        ax.set_xlabel("Date")
        fig.autofmt_xdate(rotation=45)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # --- Settings Tab ---
    def create_settings_tab(self, parent_frame):
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(1, weight=1)

        top_frame = ttk.Frame(parent_frame)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        top_frame.columnconfigure(1, weight=1)

        conn_frame = ttk.LabelFrame(top_frame, text="Connection", padding="10")
        conn_frame.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        
        ttk.Label(conn_frame, text="Port:").pack(anchor="w")
        self.port_var = tk.StringVar()
        self.port_menu = ttk.Combobox(conn_frame, textvariable=self.port_var, state="readonly")
        self.port_menu.pack(fill="x", pady=(0, 5))
        self.refresh_ports()
        ttk.Button(conn_frame, text="Refresh Ports", command=self.refresh_ports).pack(fill="x", pady=(0, 10))
        self.connect_button = ttk.Button(conn_frame, text="Connect", command=self.connect)
        self.connect_button.pack(fill="x")
        self.disconnect_button = ttk.Button(conn_frame, text="Disconnect", command=self.disconnect, state="disabled")
        self.disconnect_button.pack(fill="x")
        
        control_cal_frame = ttk.Frame(top_frame)
        control_cal_frame.grid(row=0, column=1, sticky="nsew")
        control_cal_frame.columnconfigure(0, weight=1)
        control_cal_frame.columnconfigure(1, weight=1)

        control_frame = ttk.LabelFrame(control_cal_frame, text="Device Controls", padding="10")
        control_frame.grid(row=0, column=0, sticky="nsew", padx=(0,5))
        ttk.Button(control_frame, text="Stream Weights", command=lambda: self.send_command('r')).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="Stream CoP", command=lambda: self.send_command('c')).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="Stop Stream", command=lambda: self.send_command('s')).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="Tare Scales", command=lambda: self.send_command('z')).pack(fill=tk.X, pady=2)

        cal_frame = ttk.LabelFrame(control_cal_frame, text="Quick Calibration", padding="10")
        cal_frame.grid(row=0, column=1, sticky="nsew", padx=(5,0))
        ttk.Label(cal_frame, text="Weight (lbs):").pack(anchor="w")
        self.cal_weight_var = tk.StringVar(value="10.0")
        ttk.Entry(cal_frame, textvariable=self.cal_weight_var).pack(fill=tk.X, pady=2)
        ttk.Button(cal_frame, text="Calibrate", command=self.start_calibration).pack(fill=tk.X, pady=5)
        
        bottom_frame = ttk.Frame(parent_frame)
        bottom_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        bottom_frame.rowconfigure(0, weight=1)
        bottom_frame.columnconfigure(0, weight=2)
        bottom_frame.columnconfigure(1, weight=1)

        data_frame = ttk.LabelFrame(bottom_frame, text="Live Data", padding="10")
        data_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)

        self.fig = Figure(figsize=(4, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.trail_line, = self.ax.plot([], [], 'b-', alpha=0.5)
        self.current_point_marker, = self.ax.plot([], [], 'ro', markersize=8)
        self.ax.set_xlim(-1.5, 1.5); self.ax.set_ylim(-1.5, 1.5)
        self.ax.set_xlabel("X"); self.ax.set_ylabel("Y")
        self.ax.set_title("Center of Pressure"); self.ax.grid(True)
        self.ax.set_aspect('equal', adjustable='box'); self.fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=data_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        weights_grid = ttk.Frame(data_frame)
        weights_grid.grid(row=1, column=0, pady=10)
        self.weight_labels = []
        for i, name in enumerate(["A", "B", "C", "D"]):
            ttk.Label(weights_grid, text=f"S{name}:").grid(row=0, column=i*2, padx=(10,2))
            label = ttk.Label(weights_grid, text="0.0", font=("Courier", 11), width=8)
            label.grid(row=0, column=i*2+1)
            self.weight_labels.append(label)

        log_frame = ttk.LabelFrame(bottom_frame, text="Serial Log", padding="10")
        log_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state="disabled", height=10)
        self.log_text.grid(row=0, column=0, sticky="nsew")

    # --- Serial Controller Methods ---
    def refresh_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_menu['values'] = ports
        if ports: self.port_var.set(ports[0])

    def connect(self):
        port = self.port_var.get()
        if not port:
            self.log_message("Please select a port first.")
            return

        self.serial_thread = SerialThread(port, BAUD_RATE, self.data_queue, self.log_queue)
        self.serial_thread.start()
        
        self.connect_button.config(state="disabled")
        self.disconnect_button.config(state="normal")
        self.port_menu.config(state="disabled")
        self.start_session_button.config(state="normal")
        self.routine_status_label.config(text=f"Connected to {port}", foreground="green")

    def disconnect(self):
        if self.serial_thread and self.serial_thread.is_alive():
            self.serial_thread.stop()
        
        self.connect_button.config(state="normal")
        self.disconnect_button.config(state="disabled")
        self.port_menu.config(state="normal")
        self.start_session_button.config(state="disabled")
        self.routine_status_label.config(text="Disconnected. Connect in Settings tab.", foreground="red")

    def send_command(self, cmd):
        if self.serial_thread and self.serial_thread.is_alive():
            self.serial_thread.send(cmd)
        else:
            self.log_message("Not connected.")

    def start_calibration(self):
        if not (self.serial_thread and self.serial_thread.is_alive()):
            self.log_message("Not connected.")
            return
        
        try:
            weight = float(self.cal_weight_var.get())
            self.serial_thread.start_calibration(weight)
        except ValueError:
            self.log_message("Error: Invalid calibration weight. Please enter a number.")
            
    def process_queues(self):
        """Periodically checks queues for new data and updates the GUI."""
        try:
            while not self.log_queue.empty():
                self.log_message(self.log_queue.get_nowait())
            
            while not self.data_queue.empty():
                line = self.data_queue.get_nowait()
                self.parse_and_update(line)

        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_queues)

    def parse_and_update(self, line):
        """Parses a line of data and updates the appropriate UI elements."""
        self.log_message(f"Rx: {line}")

        weight_match = self.weight_pattern.match(line)
        if weight_match:
            weights = weight_match.groups()
            for i in range(4): self.weight_labels[i].config(text=f"{float(weights[i]):.2f}")
            return

        cop_match = self.cop_pattern.match(line)
        if cop_match:
            x, y = map(float, cop_match.groups())
            self.update_cop_display(x, y)
            
            # --- MODIFIED: Data is no longer passed to the session window here ---
            # You will need to handle how data gets from this main loop 
            # to your new session window's logic.
            return

    def update_cop_display(self, x, y):
        """Updates the matplotlib plot with new CoP data."""
        self.x_com_history.append(x)
        self.y_com_history.append(y)

        if len(self.x_com_history) > self.PLOT_HISTORY_LENGTH:
            self.x_com_history.pop(0)
            self.y_com_history.pop(0)

        self.trail_line.set_data(self.x_com_history, self.y_com_history)
        self.current_point_marker.set_data([x], [y])
        self.canvas.draw_idle()

    def log_message(self, msg):
        """Appends a message to the log text area."""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END) # Auto-scroll
        self.log_text.config(state="disabled")

class LoginApp(tk.Tk):
    """The initial login window for the application."""
    def __init__(self):
        super().__init__()
        self.title("Exercise App Login")
        self.geometry("300x200")

        main_frame = tk.Frame(self)
        main_frame.pack(expand=True)
        
        main_frame.columnconfigure(1, weight=1)

        ttk.Label(main_frame, text="Username:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.username_entry = ttk.Entry(main_frame)
        self.username_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(main_frame, text="Enter PIN:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.pin_entry = ttk.Entry(main_frame, show="*")
        self.pin_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Login", command=self.handle_login).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Register", command=self.handle_register).pack(side=tk.LEFT, padx=5)

    def handle_login(self):
        username = self.username_entry.get()
        pin = self.pin_entry.get()
        success, message, full_name, gender = login_user(username, pin)
        if success:
            self.destroy()
            dashboard = Dashboard(username, full_name, gender)
            dashboard.mainloop()
        else:
            messagebox.showerror("Login Failed", message)

    def handle_register(self):
        RegistrationWindow(self)

def setup_files():
    """Ensures the necessary files and folders exist before the app runs."""
    if not os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['username', 'hashed_pin', 'first_name', 'last_name', 'gender'])
    os.makedirs(SESSION_DATA_FOLDER, exist_ok=True)

if __name__ == "__main__":
    setup_files()
    app = LoginApp()
    app.mainloop()
