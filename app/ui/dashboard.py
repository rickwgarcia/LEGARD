import tkinter as tk
from tkinter import ttk
import logging
import queue
import serial.tools.list_ports

# Import existing windows and config
from ui.windows.routine_window import RoutineWindow
from ui.windows.calibration_window import CalibrationWindow
from core.config_manager import config
from ui.tabs.history_tab import HistoryTab 
from core.data_inputs import SerialThread, SensorThread
from ui.tabs.analytics_tab import AnalyticsTab
from ui.tabs.settings_tab import SettingsTab
from ui.tabs.profile_tab import ProfileTab

# Sensor-related imports
try:
    import board
    import adafruit_bno055
except ImportError:
    print("Warning: Could not import 'board' or 'adafruit_bno055'. BNO055 sensor will not be available.")
    board = None
    adafruit_bno055 = None

"""
The main application dashboard, serving as the central hub for the GUI 
and hardware management.

It initializes the user interface (Notebook with multiple tabs) and establishes 
multithreaded connections for the serial device (e.g., balance board) and the 
I2C sensor (BNO055). It manages the lifespan of these threads and ensures 
data integrity via a shared queue.
"""

class Dashboard(tk.Tk):
    """
    The main application window hosting all functional tabs and managing 
    hardware threads.
    """
    def __init__(self, username, full_name, gender):
        """
        Initializes the Dashboard, setting up the GUI and hardware connections.

        Args:
            username (str): The logged-in user's unique username.
            full_name (str): The logged-in user's full name.
            gender (str): The logged-in user's gender.
        """
        super().__init__()
        self.username = username
        self.full_name = full_name
        self.gender = gender
        self.title(f"Exercise Dashboard - Welcome {self.full_name}")
        self.attributes('-fullscreen', True)
        self.bind('<Escape>', lambda e: self.on_closing())
        
        self.routine_window = None
        
        # Shared queue for data from both serial and sensor threads
        self.shared_queue = queue.Queue()
        
        # --- Hardware Initialization ---
        self.sensor = None
        self.init_sensor()
        self.sensor_thread = None
        if self.sensor:
            self.sensor_thread = SensorThread(self.sensor)
            self.sensor_thread.start()

        self.serial_thread = None
        port = config.get('Serial', 'port')
        baud = config.getint('Serial', 'baudrate')
        
        # Auto-detect port if not configured
        if not port:
            port = next((p.device for p in serial.tools.list_ports.comports()), None)
        
        if port:
            self.serial_thread = SerialThread(port, baud, self.shared_queue)
            self.serial_thread.start()

        # --- Notebook/Tabs Setup ---
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=20, padx=20, expand=True, fill="both")
        
        self.setup_tabs()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_tabs(self):
        """Initializes and adds all functional tabs to the Notebook widget."""
        tabs = {
            "[P] Profile": self.create_profile_tab, 
            "[R] Routine": self.create_routine_tab, 
            "[H] History": self.create_history_tab, 
            "[A] Analytics": self.create_analytics_tab, 
            "[S] Settings": self.create_settings_tab
        }
        for name, creation_func in tabs.items():
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=name)
            creation_func(frame)

    def init_sensor(self):
        """
        Initializes the BNO055 sensor object using I2C communication.

        Sets `self.sensor` to the initialized object or `None` if hardware 
        or library import fails. Logs initialization status.
        """
        if board and adafruit_bno055:
            try:
                i2c = board.I2C()
                self.sensor = adafruit_bno055.BNO055_I2C(i2c)
                logging.info("BNO055 sensor found and initialized in Dashboard.")
            except (ValueError, OSError) as e:
                logging.error(f"BNO055 sensor not found. Error: {e}")
                self.sensor = None
        else:
            self.sensor = None

    def on_closing(self):
        """
        Handles application shutdown, ensuring all running threads are safely 
        stopped before destroying the GUI.
        """
        # Clean up threads
        if self.sensor_thread: self.sensor_thread.stop()
        if self.serial_thread: 
            # Send 's' command to the serial device to signal stop/reset
            self.serial_thread.send('s')
            self.serial_thread.stop()
            
        if self.routine_window and self.routine_window.winfo_exists():
            self.routine_window.destroy()
        self.destroy()

    def create_profile_tab(self, parent_frame):
        """Instantiates and packs the ProfileTab."""
        profile = ProfileTab(parent_frame, self.username, self.full_name, self.gender)
        profile.pack(fill="both", expand=True)

    def create_routine_tab(self, parent_frame):
        """Sets up the content for the Routine tab, featuring the 'Start New Routine' button."""
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(0, weight=1)
        start_button = ttk.Button(parent_frame, text="Start New Routine", command=self.start_routine)
        start_button.grid(row=0, column=0, ipady=20, ipadx=40)

    def start_routine(self):
        """
        Starts the routine workflow by launching the CalibrationWindow.

        If a RoutineWindow already exists, it is simply brought to the front. 
        It passes all necessary thread and hardware objects to the CalibrationWindow.
        """
        if self.routine_window and self.routine_window.winfo_exists():
            self.routine_window.lift()
            return
        CalibrationWindow(
            self, 
            self.sensor, 
            self.shared_queue, 
            self.sensor_thread, 
            self.serial_thread, 
            on_complete_callback=self.launch_routine_window
        )

    def launch_routine_window(self, initial_angle, max_angle):
        """
        Callback function executed after calibration is complete. 

        Launches the main RoutineWindow, passing in the hardware objects 
        and the calibration results (initial_angle, max_angle).

        Args:
            initial_angle (float): The calibrated starting angle.
            max_angle (float): The calibrated maximum range of motion angle.
        """
        if self.routine_window and self.routine_window.winfo_exists():
            self.routine_window.lift()
            return
        self.routine_window = RoutineWindow(
            self, 
            self.username, 
            self.sensor, 
            self.shared_queue, 
            self.sensor_thread, 
            self.serial_thread,
            initial_angle, 
            max_angle
        )
        self.routine_window.focus()

    def create_history_tab(self, parent_frame):
        """Instantiates and packs the HistoryTab."""
        history_tab = HistoryTab(parent_frame, self.username)
        history_tab.pack(fill="both", expand=True)

    def create_analytics_tab(self, parent_frame):
        """Instantiates and packs the AnalyticsTab."""
        analytics = AnalyticsTab(parent_frame, self.username)
        analytics.pack(fill="both", expand=True)

    def create_settings_tab(self, parent_frame):
        """Instantiates and packs the SettingsTab."""
        settings = SettingsTab(parent_frame, self.username)
        settings.pack(fill="both", expand=True)