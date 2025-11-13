import tkinter as tk
from tkinter import ttk, messagebox
import os
import csv
import logging
from datetime import datetime
from config_manager import config  # Import the config object

# --- Imports for plotting ---
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class HistoryTab(ttk.Frame):
    """
    A ttk.Frame that contains the complete UI and logic for the History tab,
    featuring plots for CoP and Angle.
    """
    def __init__(self, parent, username, **kwargs):
        super().__init__(parent, **kwargs)

        self.username = username

        # --- Instance variables to store data ---
        self.session_files = {}  # Dict to map display names to file paths
        self.current_session_data = []  # Stores rows from the selected CSV
        self.current_session_headers = []  # Stores headers from the CSV
        self.calibrated_max_angle = None  # Store max angle from metadata

        # --- Create and pack the widgets ---
        self.setup_widgets()

        # --- Load initial data ---
        self.load_session_files()

    def setup_widgets(self):
        """
        Creates the History tab's widgets (dropdowns, plots, etc.).
        """
        # --- Top control frame ---
        control_frame = ttk.Frame(self, padding=(10, 10))
        control_frame.pack(fill='x')

        ttk.Label(control_frame, text="Session:").grid(row=0, column=0, padx=(0, 5), sticky='w')
        self.session_combo = ttk.Combobox(control_frame, state="readonly", width=30)
        self.session_combo.grid(row=0, column=1, padx=(0, 20), sticky='w')

        ttk.Label(control_frame, text="Set:").grid(row=0, column=2, padx=(0, 5), sticky='w')
        self.set_combo = ttk.Combobox(control_frame, state="disabled", width=15)
        self.set_combo.grid(row=0, column=3, padx=(0, 20), sticky='w')

        # Label to show metadata (like Max Angle)
        self.max_angle_label_var = tk.StringVar(value="Load a session.")
        ttk.Label(control_frame, textvariable=self.max_angle_label_var, font=("Helvetica", 10, "italic")).grid(row=0, column=4, sticky='w')

        control_frame.columnconfigure(4, weight=1)  # Makes the label align left

        # --- Plot display frame ---
        plot_frame = ttk.Frame(self)
        plot_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # --- Matplotlib Figure and Axes ---
        # Create the figure and subplots, matching the RoutineWindow layout
        self.fig, (self.ax_cop, self.ax_angle) = plt.subplots(
            1, 2, figsize=(9, 3), dpi=100, constrained_layout=True
        )

        # --- Embed the plot in Tkinter ---
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # --- Initialize plot appearance ---
        self.reset_plots()

        # --- Bind events ---
        self.session_combo.bind('<<ComboboxSelected>>', self.on_session_selected)
        self.set_combo.bind('<<ComboboxSelected>>', self.on_set_selected)

    def reset_plots(self, message="Select a session to load data"):
        """Clears and formats the plots to their initial state."""
        self.ax_cop.clear()
        self.ax_angle.clear()

        # Get plot limits from config
        cop_x_lim = config.getfloat('Plotting', 'cop_x_limit', fallback=10)
        cop_y_lim = config.getfloat('Plotting', 'cop_y_limit', fallback=10)
        angle_y_min = config.getfloat('Plotting', 'angle_y_min', fallback=-10)
        angle_y_max = config.getfloat('Plotting', 'angle_y_max', fallback=100)

        # Format CoP plot
        self.ax_cop.set_title("Center of Pressure")
        self.ax_cop.set_xlim(-cop_x_lim, cop_x_lim)
        self.ax_cop.set_ylim(-cop_y_lim, cop_y_lim)
        self.ax_cop.set_aspect('equal', adjustable='box')
        self.ax_cop.grid(True)
        self.ax_cop.text(0.5, 0.5, message,
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax_cop.transAxes,
                         fontdict={'color': 'gray', 'size': 12})


        # Format Angle plot
        self.ax_angle.set_title("Relative Angle")
        self.ax_angle.set_xlabel("Time (s)")
        self.ax_angle.set_ylabel("Angle (degrees)")
        self.ax_angle.set_ylim(angle_y_min, angle_y_max)
        self.ax_angle.grid(True)

        self.canvas.draw()

    def load_session_files(self):
        """Scans the user's directory for datalog files and populates the session dropdown."""
        # ... (This function is unchanged from the previous step) ...
        self.session_files = {}
        try:
            # Get the base directory from the config file
            user_sessions_dir = os.path.join(config.get('Paths', 'sessions_base_dir'), self.username)
            if not os.path.exists(user_sessions_dir):
                self.max_angle_label_var.set("No session directory found.")
                self.session_combo.config(values=[])
                return

            session_files_found = []
            for filename in os.listdir(user_sessions_dir):
                if filename.startswith('datalog_') and filename.endswith('.csv'):
                    full_path = os.path.join(user_sessions_dir, filename)
                    try:
                        # Convert filename timestamp to a readable format
                        timestamp_str = filename[8:-4] # "datalog_" is 8 chars
                        dt = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                        display_name = dt.strftime('%Y-%m-%d %H:%M:%S')
                        self.session_files[display_name] = full_path
                        session_files_found.append(display_name)
                    except ValueError:
                        logging.warning(f"Skipping file with unexpected name: {filename}")
            
            if session_files_found:
                # Sort by newest first
                self.session_combo.config(values=sorted(session_files_found, reverse=True))
                self.session_combo.set("Select a session")
                self.max_angle_label_var.set("Please select a session.")
            else:
                self.max_angle_label_var.set("No sessions found.")
                self.session_combo.config(values=[])

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load session files: {e}", parent=self)
            self.max_angle_label_var.set("Error loading sessions.")


    def on_session_selected(self, event=None):
        """Called when a new session is selected. Loads data and plots 'All Sets'."""
        selected_display_name = self.session_combo.get()
        file_path = self.session_files.get(selected_display_name)
        if not file_path:
            return

        self.current_session_data = []  # Clear old data
        self.current_session_headers = []
        self.calibrated_max_angle = None # Reset max angle
        sets = set()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)

                # Read metadata line (e.g., "Max,13.7104")
                try:
                    metadata_line = next(reader)
                    if metadata_line and metadata_line[0] == 'Max':
                        self.calibrated_max_angle = float(metadata_line[1])
                        self.max_angle_label_var.set(f"Calibrated Max Angle: {self.calibrated_max_angle:.2f}°")
                    else:
                        self.max_angle_label_var.set("Metadata not found.")
                        self.current_session_headers = metadata_line # This was the header
                except StopIteration:
                    messagebox.showerror("Error", "File is empty.", parent=self)
                    return

                # Read header line, if we haven't already
                if not self.current_session_headers:
                    self.current_session_headers = next(reader)

                # Read all data rows into memory
                set_col_idx = self.current_session_headers.index('Set')
                for row in reader:
                    if len(row) == len(self.current_session_headers):
                        self.current_session_data.append(row)
                        sets.add(row[set_col_idx])  # Add 'Set' number
                    else:
                        logging.warning(f"Skipping row with incorrect column count: {row}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {e}", parent=self)
            self.max_angle_label_var.set("Error reading file.")
            self.current_session_headers = []  # Reset on error
            return

        # Populate Set combobox
        sorted_sets = sorted(list(sets), key=lambda x: int(x) if x.isdigit() else 0)
        self.set_combo['values'] = ["All Sets"] + sorted_sets
        self.set_combo.set("All Sets")
        self.set_combo.config(state="readonly")

        # Load data for "All Sets" by default
        self.plot_data("All Sets")

    def on_set_selected(self, event=None):
        """Called when a new set is selected. Re-plots the data."""
        selected_set = self.set_combo.get()
        if not selected_set:
            return
        self.plot_data(selected_set)

    def plot_data(self, selected_set):
        """Filters self.current_session_data and populates the plots."""
        
        # Clear the axes for new data
        self.ax_cop.clear()
        self.ax_angle.clear()

        if not self.current_session_data or not self.current_session_headers:
            self.reset_plots("No data to display.")
            return

        try:
            # Find column indices
            set_idx = self.current_session_headers.index('Set')
            time_idx = self.current_session_headers.index('Time')
            angle_idx = self.current_session_headers.index('Angle')
            x_idx = self.current_session_headers.index('X')
            y_idx = self.current_session_headers.index('Y')
        except ValueError as e:
            logging.error(f"Missing expected column in CSV: {e}")
            self.reset_plots(f"Error: Missing column {e}")
            return

        times, angles, x_coords, y_coords = [], [], [], []

        # Filter data
        for row in self.current_session_data:
            if selected_set == "All Sets" or row[set_idx] == selected_set:
                try:
                    times.append(float(row[time_idx]))
                    angles.append(float(row[angle_idx]))
                    x_coords.append(float(row[x_idx]))
                    y_coords.append(float(row[y_idx]))
                except (ValueError, IndexError):
                    logging.warning(f"Skipping malformed data row: {row}")
                    continue
        
        if not times:
            self.reset_plots(f"No data found for '{selected_set}'.")
            return

        # --- Plotting ---

        # CoP Plot
        cop_x_lim = config.getfloat('Plotting', 'cop_x_limit', fallback=10)
        cop_y_lim = config.getfloat('Plotting', 'cop_y_limit', fallback=10)
        self.ax_cop.plot(x_coords, y_coords, 'b-', alpha=0.5, lw=2)
        self.ax_cop.set_xlim(-cop_x_lim, cop_x_lim)
        self.ax_cop.set_ylim(-cop_y_lim, cop_y_lim)
        self.ax_cop.set_title("Center of Pressure")
        self.ax_cop.grid(True)
        self.ax_cop.set_aspect('equal', adjustable='box')
        self.ax_cop.set_xticklabels([]) # Hide tick labels
        self.ax_cop.set_yticklabels([])

        # Angle Plot
        angle_y_min = config.getfloat('Plotting', 'angle_y_min', fallback=-10)
        angle_y_max = config.getfloat('Plotting', 'angle_y_max', fallback=100)
        self.ax_angle.plot(times, angles, 'g-')
        self.ax_angle.set_title("Relative Angle")
        self.ax_angle.set_xlabel("Time (s)")
        self.ax_angle.set_ylabel("Angle (degrees)")
        self.ax_angle.grid(True)
        self.ax_angle.set_ylim(angle_y_min, angle_y_max)
        self.ax_angle.set_xlim(min(times), max(times)) # Fit x-axis to data

        # Plot target threshold line
        if self.calibrated_max_angle is not None and self.calibrated_max_angle > 0:
            MAX_ANGLE_TOLERANCE_PERCENT = config.getfloat('RepCounter', 'max_angle_tolerance_percent', fallback=90.0)
            target_threshold = self.calibrated_max_angle * (MAX_ANGLE_TOLERANCE_PERCENT / 100.0)
            self.ax_angle.axhline(
                y=target_threshold,
                color='green',
                linestyle='--',
                linewidth=1.5,
                label=f"Target ({target_threshold:.1f}°)"
            )
            self.ax_angle.legend(loc='upper right', fontsize='small')

        self.canvas.draw()