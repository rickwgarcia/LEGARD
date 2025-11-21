import tkinter as tk
from tkinter import ttk, messagebox
import os
import csv
import logging
from datetime import datetime
from config_manager import config

# --- Imports for plotting ---
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class HistoryTab(ttk.Frame):
    """
    A ttk.Frame that contains the complete UI and logic for the History tab,
    featuring plots for CoP and Angle with interactive linked cursors.
    """
    def __init__(self, parent, username, **kwargs):
        super().__init__(parent, **kwargs)

        self.username = username

        # --- Instance variables to store data ---
        self.session_files = {}
        self.current_session_data = []
        self.current_session_headers = []
        self.calibrated_max_angle = None
        self.saved_target_angle = None
        
        # --- NEW: Variables to hold plotting data for interactivity ---
        self.times = []
        self.x_coords = []
        self.y_coords = []

        # --- NEW: References to the cursor visual elements ---
        self.cursor_line = None # The vertical line on the Angle plot
        self.cursor_dot = None  # The dot on the CoP plot

        self.setup_widgets()
        self.load_session_files()

    def setup_widgets(self):
        # --- Top control frame ---
        control_frame = ttk.Frame(self, padding=(10, 10))
        control_frame.pack(fill='x')

        ttk.Label(control_frame, text="Session:").grid(row=0, column=0, padx=(0, 5), sticky='w')
        self.session_combo = ttk.Combobox(control_frame, state="readonly", width=30)
        self.session_combo.grid(row=0, column=1, padx=(0, 20), sticky='w')

        ttk.Label(control_frame, text="Set:").grid(row=0, column=2, padx=(0, 5), sticky='w')
        self.set_combo = ttk.Combobox(control_frame, state="disabled", width=15)
        self.set_combo.grid(row=0, column=3, padx=(0, 20), sticky='w')

        self.metadata_label_var = tk.StringVar(value="Load a session.")
        meta_label = ttk.Label(control_frame, textvariable=self.metadata_label_var, font=("Helvetica", 10, "italic"))
        meta_label.grid(row=0, column=4, sticky='w')

        refresh_btn = ttk.Button(control_frame, text="Refresh Data", command=self.refresh_history)
        refresh_btn.grid(row=0, column=5, padx=(10, 0), sticky='e')

        control_frame.columnconfigure(4, weight=1) 

        # --- Plot display frame ---
        plot_frame = ttk.Frame(self)
        plot_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # --- Matplotlib Figure and Axes ---
        self.fig, (self.ax_cop, self.ax_angle) = plt.subplots(
            1, 2, figsize=(9, 3), dpi=100, constrained_layout=True
        )

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # --- NEW: Connect the click event to the handler ---
        self.canvas.mpl_connect('button_press_event', self.on_plot_click)

        self.reset_plots()

        # --- Bind events ---
        self.session_combo.bind('<<ComboboxSelected>>', self.on_session_selected)
        self.set_combo.bind('<<ComboboxSelected>>', self.on_set_selected)

    def refresh_history(self):
        self.load_session_files()
        self.set_combo.set('')
        self.set_combo.config(state="disabled")
        self.reset_plots("Data refreshed. Select a session.")

    def reset_plots(self, message="Select a session to load data"):
        """Clears and formats the plots to their initial state."""
        self.ax_cop.clear()
        self.ax_angle.clear()

        # --- NEW: Reset cursor references ---
        self.cursor_line = None
        self.cursor_dot = None

        cop_x_lim = config.getfloat('Plotting', 'cop_x_limit', fallback=10)
        cop_y_lim = config.getfloat('Plotting', 'cop_y_limit', fallback=10)
        angle_y_min = config.getfloat('Plotting', 'angle_y_min', fallback=-10)
        angle_y_max = config.getfloat('Plotting', 'angle_y_max', fallback=100)

        self.ax_cop.set_title("Center of Pressure")
        self.ax_cop.set_xlim(-cop_x_lim, cop_x_lim)
        self.ax_cop.set_ylim(-cop_y_lim, cop_y_lim)
        self.ax_cop.set_aspect('equal', adjustable='box')
        self.ax_cop.grid(True)
        self.ax_cop.text(0.5, 0.5, message,
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax_cop.transAxes,
                         fontdict={'color': 'gray', 'size': 12})

        self.ax_angle.set_title("Relative Angle")
        self.ax_angle.set_xlabel("Time (s)")
        self.ax_angle.set_ylabel("Angle (degrees)")
        self.ax_angle.set_ylim(angle_y_min, angle_y_max)
        self.ax_angle.grid(True)

        self.canvas.draw()

    def load_session_files(self):
        # (No changes to this method)
        self.session_files = {}
        try:
            user_sessions_dir = os.path.join(config.get('Paths', 'sessions_base_dir'), self.username)
            if not os.path.exists(user_sessions_dir):
                self.metadata_label_var.set("No session directory found.")
                self.session_combo.config(values=[])
                return

            session_files_found = []
            for filename in os.listdir(user_sessions_dir):
                if filename.startswith('datalog_') and filename.endswith('.csv'):
                    full_path = os.path.join(user_sessions_dir, filename)
                    try:
                        timestamp_str = filename[8:-4] 
                        dt = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                        display_name = dt.strftime('%Y-%m-%d %H:%M:%S')
                        self.session_files[display_name] = full_path
                        session_files_found.append(display_name)
                    except ValueError:
                        logging.warning(f"Skipping file with unexpected name: {filename}")
            
            if session_files_found:
                self.session_combo.config(values=sorted(session_files_found, reverse=True))
                self.session_combo.set("Select a session")
                self.metadata_label_var.set("Please select a session.")
            else:
                self.metadata_label_var.set("No sessions found.")
                self.session_combo.config(values=[])

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load session files: {e}", parent=self)
            self.metadata_label_var.set("Error loading sessions.")

    def on_session_selected(self, event=None):
        # (No changes to this method logic, just ensuring it calls plot_data)
        selected_display_name = self.session_combo.get()
        file_path = self.session_files.get(selected_display_name)
        if not file_path:
            return

        self.current_session_data = []  
        self.current_session_headers = []
        self.calibrated_max_angle = None 
        self.saved_target_angle = None 
        sets = set()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                try:
                    line1 = next(reader)
                    if line1 and line1[0] == 'Max':
                        self.calibrated_max_angle = float(line1[1])
                    else:
                        self.current_session_headers = line1 
                except StopIteration:
                    messagebox.showerror("Error", "File is empty.", parent=self)
                    return

                if not self.current_session_headers:
                    try:
                        line2 = next(reader)
                        if line2 and line2[0] == 'Target':
                            self.saved_target_angle = float(line2[1])
                            self.current_session_headers = next(reader)
                        else:
                            self.current_session_headers = line2
                    except StopIteration:
                        pass 

                meta_text = ""
                if self.calibrated_max_angle:
                    meta_text += f"Max: {self.calibrated_max_angle:.1f}°"
                if self.saved_target_angle:
                    meta_text += f" | Target: {self.saved_target_angle:.1f}°"
                self.metadata_label_var.set(meta_text if meta_text else "No metadata found.")

                if self.current_session_headers and 'Set' in self.current_session_headers:
                    set_col_idx = self.current_session_headers.index('Set')
                    for row in reader:
                        if len(row) == len(self.current_session_headers):
                            self.current_session_data.append(row)
                            sets.add(row[set_col_idx])  
                        else:
                            logging.warning(f"Skipping row with incorrect column count: {row}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {e}", parent=self)
            self.metadata_label_var.set("Error reading file.")
            self.current_session_headers = []  
            return

        sorted_sets = sorted(list(sets), key=lambda x: int(x) if x.isdigit() else 0)
        self.set_combo['values'] = ["All Sets"] + sorted_sets
        self.set_combo.set("All Sets")
        self.set_combo.config(state="readonly")

        self.plot_data("All Sets")

    def on_set_selected(self, event=None):
        selected_set = self.set_combo.get()
        if not selected_set:
            return
        self.plot_data(selected_set)

    def plot_data(self, selected_set):
        self.ax_cop.clear()
        self.ax_angle.clear()

        # --- NEW: Reset cursors when plotting new data ---
        self.cursor_line = None
        self.cursor_dot = None

        if not self.current_session_data or not self.current_session_headers:
            self.reset_plots("No data to display.")
            return

        try:
            set_idx = self.current_session_headers.index('Set')
            time_idx = self.current_session_headers.index('Time')
            angle_idx = self.current_session_headers.index('Angle')
            x_idx = self.current_session_headers.index('X')
            y_idx = self.current_session_headers.index('Y')
        except ValueError as e:
            logging.error(f"Missing expected column in CSV: {e}")
            self.reset_plots(f"Error: Missing column {e}")
            return

        # --- UPDATED: Clear previous instance data ---
        self.times = []
        self.x_coords = []
        self.y_coords = []
        # We can keep angles local if we don't need to look them up on click
        angles = [] 

        for row in self.current_session_data:
            if selected_set == "All Sets" or row[set_idx] == selected_set:
                try:
                    # --- UPDATED: Populate instance variables ---
                    self.times.append(float(row[time_idx]))
                    self.x_coords.append(float(row[x_idx]))
                    self.y_coords.append(float(row[y_idx]))
                    angles.append(float(row[angle_idx]))
                except (ValueError, IndexError):
                    continue
        
        if not self.times:
            self.reset_plots(f"No data found for '{selected_set}'.")
            return

        cop_x_lim = config.getfloat('Plotting', 'cop_x_limit', fallback=10)
        cop_y_lim = config.getfloat('Plotting', 'cop_y_limit', fallback=10)
        
        # Use self.x_coords / self.y_coords here
        self.ax_cop.plot(self.x_coords, self.y_coords, 'b-', alpha=0.5, lw=2)
        self.ax_cop.set_xlim(-cop_x_lim, cop_x_lim)
        self.ax_cop.set_ylim(-cop_y_lim, cop_y_lim)
        self.ax_cop.set_title("Center of Pressure")
        self.ax_cop.grid(True)
        self.ax_cop.set_aspect('equal', adjustable='box')
        self.ax_cop.set_xticklabels([])
        self.ax_cop.set_yticklabels([])

        angle_y_min = config.getfloat('Plotting', 'angle_y_min', fallback=-10)
        angle_y_max = config.getfloat('Plotting', 'angle_y_max', fallback=100)
        
        # Use self.times here
        self.ax_angle.plot(self.times, angles, 'g-')
        self.ax_angle.set_title("Relative Angle")
        self.ax_angle.set_xlabel("Time (s)")
        self.ax_angle.set_ylabel("Angle (degrees)")
        self.ax_angle.grid(True)
        self.ax_angle.set_ylim(angle_y_min, angle_y_max)
        self.ax_angle.set_xlim(min(self.times), max(self.times))

        target_to_plot = None
        if self.saved_target_angle is not None:
            target_to_plot = self.saved_target_angle
            label_text = f"Target ({target_to_plot:.1f}°)"
        elif self.calibrated_max_angle is not None and self.calibrated_max_angle > 0:
            MAX_ANGLE_TOLERANCE_PERCENT = config.getfloat('RepCounter', 'max_angle_tolerance_percent', fallback=90.0)
            target_to_plot = self.calibrated_max_angle * (MAX_ANGLE_TOLERANCE_PERCENT / 100.0)
            label_text = f"Calc Target ({target_to_plot:.1f}°)"

        if target_to_plot:
            self.ax_angle.axhline(y=target_to_plot, color='green', linestyle='--', linewidth=1.5, label=label_text)
            self.ax_angle.legend(loc='upper right', fontsize='small')

        self.canvas.draw()

    # --- NEW: Event Handler Function ---
    def on_plot_click(self, event):
        """
        Handles mouse clicks on the plots.
        If the Angle plot is clicked:
          1. Find the closest time index.
          2. Draw a vertical line on the Angle plot.
          3. Draw a dot on the CoP plot corresponding to that index.
        """
        # 1. Check if the click happened inside the Angle axes and if we have data
        if event.inaxes != self.ax_angle or not self.times:
            return

        # 2. Get the time (x-value) from the click
        clicked_time = event.xdata

        # 3. Find the index in self.times closest to clicked_time
        # This uses min with a key function to find the smallest difference
        closest_index = min(
            range(len(self.times)), 
            key=lambda i: abs(self.times[i] - clicked_time)
        )

        # 4. Retrieve the data at that index
        actual_time = self.times[closest_index]
        cop_x = self.x_coords[closest_index]
        cop_y = self.y_coords[closest_index]

        # 5. Update the Vertical Line (Angle Plot)
        if self.cursor_line:
            # If line exists, just move it (faster than removing and replotting)
            self.cursor_line.set_xdata([actual_time, actual_time])
        else:
            # Create the line if it doesn't exist
            self.cursor_line = self.ax_angle.axvline(x=actual_time, color='red', alpha=0.8, lw=2)

        # 6. Update the Dot (CoP Plot)
        if self.cursor_dot:
            # If dot exists, update position
            self.cursor_dot.set_data([cop_x], [cop_y])
        else:
            # Create the dot (plot returns a list of lines, we take the first one)
            self.cursor_dot, = self.ax_cop.plot(cop_x, cop_y, 'ro', markersize=8, zorder=5)

        # 7. Redraw the canvas to show changes
        self.canvas.draw()