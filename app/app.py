import csv
import hashlib
import os
import tkinter as tk
from tkinter import messagebox, ttk
import logging

# Import the new windows and config manager
from routine_window import RoutineWindow
from calibration_window import CalibrationWindow
from config_manager import config

# Sensor-related imports
try:
    import board
    import adafruit_bno055
except ImportError:
    print("Warning: Could not import 'board' or 'adafruit_bno055'. BNO055 sensor will not be available.")
    board = None
    adafruit_bno055 = None


# --- Constants ---
USER_DATA_FILE = config.get('Paths', 'user_data_file')

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
    
    os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
    
    # Check for header before checking for users
    if not os.path.exists(USER_DATA_FILE):
        setup_files() # Ensure file and header exist

    with open(USER_DATA_FILE, 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader) # Skip header
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
        
    if not os.path.exists(USER_DATA_FILE):
        return (False, "No user accounts found. Please register an account.", None, None)
        
    hashed_pin = hash_pin(pin)
    with open(USER_DATA_FILE, 'r', newline='') as file:
        reader = csv.reader(file)
        try:
            next(reader) # Skip header
        except StopIteration:
            return (False, "No user accounts found.", None, None)

        for row in reader:
            if len(row) >= 5 and row[0] == username and row[1] == hashed_pin:
                full_name = f"{row[2]} {row[3]}"
                gender = row[4]
                return (True, f"Welcome back, {full_name}!", full_name, gender)
                
    return (False, "Invalid username or PIN.", None, None)

# --- GUI Classes ---
class RegistrationWindow(tk.Toplevel):
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

class Dashboard(tk.Tk):
    def __init__(self, username, full_name, gender):
        super().__init__()
        self.username = username
        self.full_name = full_name
        self.gender = gender
        self.title(f"Exercise Dashboard - Welcome {self.full_name}")
        self.attributes('-fullscreen', True)
        self.bind('<Escape>', lambda e: self.on_closing())
        
        self.routine_window = None
        self.sensor = None
        self.init_sensor() # Initialize sensor when dashboard opens

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=20, padx=20, expand=True, fill="both")
        tabs = {"[P] Profile": self.create_profile_tab, "[R] Routine": self.create_routine_tab, "[H] History": self.create_history_tab, "[A] Analytics": self.create_analytics_tab, "[S] Settings": self.create_settings_tab}
        for name, creation_func in tabs.items():
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=name)
            creation_func(frame)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def init_sensor(self):
        """Initializes the BNO055 sensor."""
        if board and adafruit_bno055:
            try:
                i2c = board.I2C()
                self.sensor = adafruit_bno055.BNO055_I2C(i2c)
                logging.info("BNO055 sensor found and initialized in Dashboard.")
            except (ValueError, OSError) as e:
                logging.error(f"BNO055 sensor not found. Angle data will be unavailable. Error: {e}")
                self.sensor = None
        else:
            self.sensor = None
            logging.warning("BNO055 libraries not imported. Sensor functionality disabled.")

    def on_closing(self):
        if self.routine_window and self.routine_window.winfo_exists():
            self.routine_window.destroy()
        self.destroy()

    def create_profile_tab(self, parent_frame):
        ttk.Label(parent_frame, text=f"Welcome, {self.full_name}!", font=("Helvetica", 16)).pack(pady=20)
        info_frame = ttk.Frame(parent_frame)
        info_frame.pack()
        ttk.Label(info_frame, text="Username:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(info_frame, text=self.username).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        ttk.Label(info_frame, text="Gender:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(info_frame, text=self.gender).grid(row=1, column=1, sticky="w", padx=5, pady=2)

    def create_routine_tab(self, parent_frame):
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(0, weight=1)
        start_button = ttk.Button(parent_frame, text="Start New Routine", command=self.start_routine)
        start_button.grid(row=0, column=0, ipady=20, ipadx=40)

    def start_routine(self):
        """Opens the calibration window first."""
        if self.routine_window and self.routine_window.winfo_exists():
            self.routine_window.lift()
            return
            
        # Instead of opening RoutineWindow directly, open the calibration window
        CalibrationWindow(self, self.sensor, on_complete_callback=self.launch_routine_window)

    def launch_routine_window(self, initial_angle):
        """
        This is the callback function called by CalibrationWindow.
        It receives the calibration result and opens the main routine window.
        """
        if self.routine_window and self.routine_window.winfo_exists():
            self.routine_window.lift()
            return
        
        # Now, create the routine window and pass the sensor and initial angle to it
        self.routine_window = RoutineWindow(self, self.username, self.sensor, initial_angle)
        self.routine_window.focus()

    def create_history_tab(self, parent_frame):
        ttk.Label(parent_frame, text="Workout history will be displayed here.", font=("Helvetica", 14), foreground="gray").pack(expand=True)

    def create_analytics_tab(self, parent_frame):
        ttk.Label(parent_frame, text="Performance analytics will be shown here.", font=("Helvetica", 14), foreground="gray").pack(expand=True)

    def create_settings_tab(self, parent_frame):
        ttk.Label(parent_frame, text="Application settings will be configured here.", font=("Helvetica", 14), foreground="gray").pack(expand=True)

class LoginApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Exercise App Login")
        self.attributes('-fullscreen', True)
        self.bind('<Escape>', lambda e: self.destroy())
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
    """Ensures the necessary user data file and directory exist."""
    user_dir = os.path.dirname(USER_DATA_FILE)
    if user_dir and not os.path.exists(user_dir):
        os.makedirs(user_dir)
        
    if not os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['username', 'hashed_pin', 'first_name', 'last_name', 'gender'])

if __name__ == "__main__":
    setup_files()
    app = LoginApp()
    app.mainloop()