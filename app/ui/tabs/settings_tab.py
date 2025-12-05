import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import serial.tools.list_ports
import os
import sys
import platform
import subprocess

# Import the shared config object
from core.config_manager import config

"""
Module containing the SettingsTab, a comprehensive Tkinter frame for managing 
application configuration settings, including hardware connection parameters, 
algorithm tuning, and data management controls.
"""

class SettingsTab(ttk.Frame):
    """
    A Tkinter tab component that provides a user interface for viewing, 
    modifying, and saving application configuration settings.
    
    It interacts directly with the `config_manager` and provides features 
    like restoring defaults, refreshing serial ports, and accessing log folders.
    """
    def __init__(self, parent, username):
        """
        Initializes the SettingsTab.

        Args:
            parent (ttk.Notebook): The Notebook widget this tab belongs to.
            username (str): The username of the currently logged-in user, used 
                            for locating user-specific log folders.
        """
        super().__init__(parent)
        self.username = username
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Dictionary to hold the Tkinter variables for easy retrieval
        self.vars = {}
        
        # List to store help text for the Info Window
        self.help_info = []
        
        self.create_layout()
        self.load_current_values()

    def create_layout(self):
        """
        Constructs the main UI layout, organizing controls into header, 
        left column (Hardware, Paths), and right column (Algorithm, Plotting).
        """
        # ================= TOP HEADER (Controls) =================
        header_frame = ttk.Frame(self)
        header_frame.pack(side="top", fill="x", pady=(0, 20))

        # Info Button (Top Left)
        info_btn = ttk.Button(header_frame, text="ℹ️ Information", command=self.show_info_window)
        info_btn.pack(side="left", padx=5)

        # Right Side Controls (Save, Restore, Label)
        save_btn = ttk.Button(header_frame, text="Save", command=self.save_settings)
        save_btn.pack(side="right", padx=(5, 0))

        restore_btn = ttk.Button(header_frame, text="Restore Defaults", command=self.restore_defaults)
        restore_btn.pack(side="right", padx=(5, 5))

        lbl = ttk.Label(header_frame, text="", 
                        font=("Arial", 9, "italic"), foreground="gray")
        lbl.pack(side="right", padx=15)

        # ================= MAIN CONTENT (Two Columns) =================
        left_col = ttk.Frame(self)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        right_col = ttk.Frame(self)
        right_col.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # ================= LEFT COLUMN =================

        # 1. Hardware Connection Settings
        hw_frame = ttk.LabelFrame(left_col, text="Hardware Connection", padding=15)
        hw_frame.pack(fill="x", pady=(0, 15))

        # COM Port Dropdown
        ttk.Label(hw_frame, text="Serial Port:").grid(row=0, column=0, sticky="w", pady=5)
        
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.vars['port'] = tk.StringVar()
        self.port_cb = ttk.Combobox(hw_frame, textvariable=self.vars['port'], values=ports)
        self.port_cb.grid(row=0, column=1, sticky="ew", padx=5)
        
        refresh_btn = ttk.Button(hw_frame, text="↻", width=3, command=self.refresh_ports)
        refresh_btn.grid(row=0, column=2, sticky="w")

        # Baudrate
        ttk.Label(hw_frame, text="Baudrate:").grid(row=1, column=0, sticky="w", pady=5)
        self.vars['baudrate'] = tk.StringVar()
        ttk.Entry(hw_frame, textvariable=self.vars['baudrate']).grid(row=1, column=1, sticky="ew", padx=5)

        hw_frame.columnconfigure(1, weight=1)

        # 2. Data & Paths
        path_frame = ttk.LabelFrame(left_col, text="Data Management", padding=15)
        path_frame.pack(fill="x", pady=(0, 15))

        # Button to open specific user logs
        open_btn = ttk.Button(path_frame, text=f"Open Session Logs", command=self.open_logs_folder)
        open_btn.pack(fill="x", pady=5)

        # ================= RIGHT COLUMN =================

        # 3. Algorithm / Rep Detection Tuning
        algo_frame = ttk.LabelFrame(right_col, text="Exercise Detection Algorithm", padding=15)
        algo_frame.pack(fill="x", pady=(0, 15))

        self.create_entry_row(algo_frame, 0, "Smoothing Window:", 'smoothing_window', 
                              "This averages sensor data to remove jitters.\n- Higher number = smoother lines but more delay (lag).\n- Lower number = very responsive but 'noisy'.\nDefault: 7")
        
        self.create_entry_row(algo_frame, 1, "Start Velocity:", 'velocity_pos_threshold',
                              "How fast you must move to START a repetition.\n- Lower number = more sensitive (easier to start).\n- Higher number = requires faster movement.\nDefault: 10.0")

        self.create_entry_row(algo_frame, 2, "Return Velocity:", 'velocity_neg_threshold',
                              "How fast you must move DOWN to register the return.\n- Must be a negative number.\nDefault: -10.0")
        
        self.create_entry_row(algo_frame, 3, "Target Angle (%):", 'max_angle_tolerance_percent',
                              "How close to your calibration max you must get to count a rep.\n- Example: 90 means you must reach 90% of your max height.\nDefault: 90")

        algo_frame.columnconfigure(1, weight=1)

        # 4. Plotting Visuals
        plot_frame = ttk.LabelFrame(right_col, text="Graph Visuals", padding=15)
        plot_frame.pack(fill="x", pady=(0, 15))

        self.create_entry_row(plot_frame, 0, "Time Window (s):", 'time_window_seconds',
                              "The number of seconds displayed on the live graph.\n- Increase to see more history.\nDefault: 5")
        
        plot_frame.columnconfigure(1, weight=1)

    def create_entry_row(self, parent, row, label_text, var_key, tooltip=""):
        """
        Creates a labeled entry field row and stores the Tkinter variable and 
        help text.

        Args:
            parent (ttk.Frame): The frame to place the widgets in.
            row (int): The grid row number.
            label_text (str): The label text for the setting.
            var_key (str): The key used to store and retrieve the Tkinter variable.
            tooltip (str): The descriptive text for the help window.
        """
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky="w", pady=5)
        self.vars[var_key] = tk.StringVar()
        ent = ttk.Entry(parent, textvariable=self.vars[var_key])
        ent.grid(row=row, column=1, sticky="ew", padx=5)
        
        # Store the label and tooltip for the Info Window
        if tooltip:
            clean_name = label_text.replace(":", "")
            self.help_info.append((clean_name, tooltip))

    def show_info_window(self):
        """Creates a full-screen, scrollable Toplevel window displaying detailed help information for all settings."""
        info_win = tk.Toplevel(self)
        info_win.title("Settings Guide")
        
        # Make Full Screen & Bind Escape
        info_win.attributes('-fullscreen', True)
        info_win.bind('<Escape>', lambda e: info_win.destroy())

        # Style for the info window
        style = ttk.Style()
        style.configure("InfoTitle.TLabel", font=("Helvetica", 24, "bold"))
        style.configure("InfoHeader.TLabel", font=("Helvetica", 16, "bold"), foreground="#333")
        style.configure("InfoBody.TLabel", font=("Arial", 14))

        # Main container
        main_container = ttk.Frame(info_win, padding=20)
        main_container.pack(fill="both", expand=True)

        # Title (Centered)
        ttk.Label(main_container, text="Settings Definitions", style="InfoTitle.TLabel").pack(pady=(20, 20), anchor="center")

        # Scrollable Canvas Setup
        canvas = tk.Canvas(main_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        def _configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(frame_id, width=event.width)

        frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", _configure_canvas)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Content Population
        content_wrapper = ttk.Frame(scrollable_frame)
        content_wrapper.pack(expand=True, fill="x", padx=50)

        for name, desc in self.help_info:
            frame = ttk.Frame(content_wrapper)
            frame.pack(fill="x", pady=15)
            
            # Name (Centered)
            ttk.Label(frame, text=name, style="InfoHeader.TLabel").pack(anchor="center")
            
            # Description (Centered)
            ttk.Label(frame, text=desc, style="InfoBody.TLabel", wraplength=900, justify="center").pack(anchor="center", pady=(5, 10))
            
            ttk.Separator(frame, orient="horizontal").pack(fill="x", padx=100)

        # Bottom Close Button (Centered)
        ttk.Button(content_wrapper, text="Close Info (ESC)", command=info_win.destroy).pack(pady=40, anchor="center")

    def refresh_ports(self):
        """Scans for and updates the list of available serial ports in the combobox."""
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_cb['values'] = ports
        if ports:
            self.port_cb.current(0)

    def open_logs_folder(self):
        """
        Opens the currently logged-in user's session data folder in the 
        native file explorer (Finder, Explorer, xdg-open). 
        Creates the folder if it does not exist.
        """
        base_path = config.get('Paths', 'sessions_base_dir', fallback='./user_sessions')
        
        # Append username to path
        user_path = os.path.join(base_path, self.username)
        
        if not os.path.exists(user_path):
            try:
                os.makedirs(user_path)
            except OSError as e:
                messagebox.showerror("Error", f"Could not create folder: {e}")
                return
            
        # Use OS-specific commands to open the folder
        if platform.system() == "Windows":
            subprocess.Popen(["start", user_path], shell=True) # Use 'start' command in Windows
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", user_path])
        else: # Linux/Unix
            subprocess.Popen(["xdg-open", user_path])

    def load_current_values(self):
        """Reads configuration values from the shared `config` object and populates all Tkinter entry fields."""
        try:
            # Serial
            self.vars['port'].set(config.get('Serial', 'port', fallback=''))
            self.vars['baudrate'].set(config.get('Serial', 'baudrate', fallback='115200'))
            
            # Algo (RepCounter)
            self.vars['smoothing_window'].set(config.get('RepCounter', 'smoothing_window', fallback='7'))
            self.vars['velocity_pos_threshold'].set(config.get('RepCounter', 'velocity_pos_threshold', fallback='10.0'))
            self.vars['velocity_neg_threshold'].set(config.get('RepCounter', 'velocity_neg_threshold', fallback='-10.0'))
            self.vars['max_angle_tolerance_percent'].set(config.get('RepCounter', 'max_angle_tolerance_percent', fallback='90.0'))
            
            # Plotting
            self.vars['time_window_seconds'].set(config.get('Plotting', 'time_window_seconds', fallback='5'))
            
        except Exception as e:
            print(f"Error loading settings: {e}")

    def restore_defaults(self):
        """
        Resets the Tkinter entry variables (not the configuration file) to 
        hardcoded default values after user confirmation.
        """
        confirm = messagebox.askyesno("Confirm Reset", "Are you sure you want to restore ALL settings to their default values?\n")
        if confirm:
            # Hardcoded Defaults
            self.vars['baudrate'].set('115200')
            self.vars['smoothing_window'].set('7')
            self.vars['velocity_pos_threshold'].set('10.0')
            self.vars['velocity_neg_threshold'].set('-10.0')
            self.vars['max_angle_tolerance_percent'].set('90.0')
            self.vars['time_window_seconds'].set('5')
            
            # Reset Port to Empty (enables auto-detect on restart)
            self.vars['port'].set('')

    def save_settings(self):
        """
        Retrieves all values from the Tkinter variables, updates the in-memory 
        config object, and writes the changes to the 'config.ini' file.
        """
        try:
            # Update config object sections
            config.set('Serial', 'port', self.vars['port'].get())
            config.set('Serial', 'baudrate', self.vars['baudrate'].get())
            
            config.set('RepCounter', 'smoothing_window', self.vars['smoothing_window'].get())
            config.set('RepCounter', 'velocity_pos_threshold', self.vars['velocity_pos_threshold'].get())
            config.set('RepCounter', 'velocity_neg_threshold', self.vars['velocity_neg_threshold'].get())
            config.set('RepCounter', 'max_angle_tolerance_percent', self.vars['max_angle_tolerance_percent'].get())
            
            config.set('Plotting', 'time_window_seconds', self.vars['time_window_seconds'].get())

            # Save to file (assuming config.ini is in the current working directory)
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
                
            messagebox.showinfo("Success", "Settings saved successfully. App restart required.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")