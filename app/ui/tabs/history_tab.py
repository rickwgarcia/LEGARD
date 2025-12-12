import tkinter as tk
from tkinter import ttk, messagebox
import os
import csv
import logging
from datetime import datetime
from core.config_manager import config
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------------
# File: history_tab.py
# Author: Ricardo Garcia, ricardo.garcia@cosmiac.org
# Last Modified: 2025-12-12
# Version: 2.0.0
# ---------------------

"""
Module containing the HistoryTab, a Tkinter frame dedicated to viewing 
the detailed raw data of previously recorded exercise sessions.
"""

class HistoryTab(ttk.Frame):
    """
    A Tkinter tab component that allows users to select and view the 
    Center of Pressure (CoP) and Angle data for a specific session and set.

    It includes an interactive scrubbing feature that links a cursor across 
    both plots based on time.
    """
    def __init__(self, parent, username, **kwargs):
        """
        Initializes the HistoryTab.

        Args:
            parent (ttk.Notebook): The Notebook widget this tab belongs to.
            username (str): The username of the currently logged-in user.
        """
        super().__init__(parent, **kwargs)

        self.username = username

        # Instance variables to store data
        self.session_files = {} # Maps display name to full file path
        self.current_session_data = [] # Raw rows of data for the selected session
        self.current_session_headers = []
        self.calibrated_max_angle = None
        self.saved_target_angle = None
        
        # Variables to hold plotting data for interactivity (all synchronized by index)
        self.times = []
        self.angles = []
        self.x_coords = [] # CoP X-coordinates
        self.y_coords = [] # CoP Y-coordinates

        # References to the cursor visual elements
        self.cursor_angle_dot = None # The dot on the Angle plot
        self.cursor_cop_dot = None   # The dot on the CoP plot
        self.is_dragging = False     # Track if mouse button is held down

        self.setup_widgets()
        self.load_session_files()

    def setup_widgets(self):
        """Sets up the Tkinter layout, including the data selectors and the Matplotlib canvas."""
        # Top control frame
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

        # Plot display frame
        plot_frame = ttk.Frame(self)
        plot_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Matplotlib Figure and Axes: Two subplots side-by-side
        self.fig, (self.ax_cop, self.ax_angle) = plt.subplots(
            1, 2, figsize=(9, 3), dpi=100, constrained_layout=True
        )

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        

        # Connect Events for Dragging/Scrubbing
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.canvas.mpl_connect('button_release_event', self.on_release)

        self.reset_plots()

        # Bind events
        self.session_combo.bind('<<ComboboxSelected>>', self.on_session_selected)
        self.set_combo.bind('<<ComboboxSelected>>', self.on_set_selected)

    def refresh_history(self):
        """Clears the current view, reloads the list of available session files, and resets the plots."""
        self.load_session_files()
        self.set_combo.set('')
        self.set_combo.config(state="disabled")
        self.reset_plots("Data refreshed. Select a session.")

    def reset_plots(self, message="Select a session to load data"):
        """Clears both plot axes and sets them to their default, empty state."""
        self.ax_cop.clear()
        self.ax_angle.clear()

        # Reset cursor references
        self.cursor_angle_dot = None
        self.cursor_cop_dot = None
        self.is_dragging = False

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
        """Scans the user's session directory and populates the session combobox."""
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
                        # Extract timestamp from filename format: datalog_YYYYMMDD_HHMMSS.csv
                        timestamp_str = filename[8:-4] 
                        dt = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                        display_name = dt.strftime('%Y-%m-%d %H:%M:%S')
                        self.session_files[display_name] = full_path
                        session_files_found.append(display_name)
                    except ValueError:
                        logging.warning(f"Skipping file with unexpected name: {filename}")
            
            if session_files_found:
                # Display the most recent sessions first
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
        """
        Event handler for the session combobox selection.

        Parses the selected CSV file, extracts metadata and all raw data rows, 
        and populates the set combobox.
        """
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
                    # Parse metadata (Max angle)
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
                        # Parse metadata (Target angle) and get headers
                        line2 = next(reader)
                        if line2 and line2[0] == 'Target':
                            self.saved_target_angle = float(line2[1])
                            self.current_session_headers = next(reader)
                        else:
                            self.current_session_headers = line2
                    except StopIteration:
                        pass 

                # Update metadata label
                meta_text = ""
                if self.calibrated_max_angle:
                    meta_text += f"Max: {self.calibrated_max_angle:.1f}°"
                if self.saved_target_angle:
                    meta_text += f" | Target: {self.saved_target_angle:.1f}°"
                self.metadata_label_var.set(meta_text if meta_text else "No metadata found.")

                # Read remaining data rows
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
        
        # --- MODIFIED CODE START ---
        self.set_combo['values'] = sorted_sets # Removed: ["All Sets"] + 
        
        if sorted_sets:
            self.set_combo.set(sorted_sets[0]) # Set the default to the first set
            self.set_combo.config(state="readonly")
            self.plot_data(sorted_sets[0])
        else:
            self.set_combo.set('') # No sets found
            self.set_combo.config(state="disabled")
            self.reset_plots("Session loaded, but no sets found.")
            
        # --- MODIFIED CODE END ---

    def on_set_selected(self, event=None):
        """Event handler for the set combobox selection; triggers plotting of the selected set."""
        selected_set = self.set_combo.get()
        if not selected_set:
            return
        self.plot_data(selected_set)

    def plot_data(self, selected_set):
        """
        Filters the raw data by the selected set, extracts the plotting vectors, 
        and redraws both the CoP and Angle charts.
        """
        self.ax_cop.clear()
        self.ax_angle.clear()

        # Reset cursors when plotting new data
        self.cursor_angle_dot = None
        self.cursor_cop_dot = None
        self.is_dragging = False

        if not self.current_session_data or not self.current_session_headers:
            self.reset_plots("No data to display.")
            return

        try:
            # Get column indices
            set_idx = self.current_session_headers.index('Set')
            time_idx = self.current_session_headers.index('Time')
            angle_idx = self.current_session_headers.index('Angle')
            x_idx = self.current_session_headers.index('X')
            y_idx = self.current_session_headers.index('Y')
        except ValueError as e:
            logging.error(f"Missing expected column in CSV: {e}")
            self.reset_plots(f"Error: Missing column {e}")
            return

        # Clear previous instance data
        self.times = []
        self.angles = []
        self.x_coords = []
        self.y_coords = []

        # Filter data based on selected set
        # Since 'selected_set' will now always be a specific set number (e.g., '1', '2'), 
        # the 'All Sets' check is effectively removed for filtering.
        for row in self.current_session_data:
            if row[set_idx] == selected_set: # Simplified filtering
                try:
                    self.times.append(float(row[time_idx]))
                    self.angles.append(float(row[angle_idx]))
                    self.x_coords.append(float(row[x_idx]))
                    self.y_coords.append(float(row[y_idx]))
                except (ValueError, IndexError):
                    continue
        
        if not self.times:
            self.reset_plots(f"No data found for '{selected_set}'.")
            return

        # --- CoP Plot (X vs Y) ---
        cop_x_lim = config.getfloat('Plotting', 'cop_x_limit', fallback=10)
        cop_y_lim = config.getfloat('Plotting', 'cop_y_limit', fallback=10)
        
        self.ax_cop.plot(self.x_coords, self.y_coords, 'b-', alpha=0.5, lw=2)
        self.ax_cop.set_xlim(-cop_x_lim, cop_x_lim)
        self.ax_cop.set_ylim(-cop_y_lim, cop_y_lim)
        self.ax_cop.set_title("Center of Pressure")
        self.ax_cop.grid(True)
        self.ax_cop.set_aspect('equal', adjustable='box')
        self.ax_cop.set_xticklabels([])
        self.ax_cop.set_yticklabels([])

        # --- Angle Plot (Angle vs Time) ---
        angle_y_min = config.getfloat('Plotting', 'angle_y_min', fallback=-10)
        angle_y_max = config.getfloat('Plotting', 'angle_y_max', fallback=100)
        
        self.ax_angle.plot(self.times, self.angles, 'g-')
        self.ax_angle.set_title("Relative Angle")
        self.ax_angle.set_xlabel("Time (s)")
        self.ax_angle.set_ylabel("Angle (degrees)")
        self.ax_angle.grid(True)
        self.ax_angle.set_ylim(angle_y_min, angle_y_max)
        self.ax_angle.set_xlim(min(self.times), max(self.times))

        # Add Target/Max Line
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

    # --- INTERACTIVE CURSOR LOGIC ---

    def update_cursors(self, x_input):
        """
        Updates the position of the marker dots on both plots based on a time 
        value (`x_input`) derived from the mouse position.

        It finds the nearest data point in time and uses its corresponding 
        angle and CoP coordinates for the dot positions.

        Args:
            x_input (float): The time value (x-coordinate) from the mouse event on the angle plot.
        """
        if not self.times:
            return

        # 1. Find nearest index
        # Finds the index with the minimum absolute difference from x_input
        idx = min(range(len(self.times)), key=lambda i: abs(self.times[i] - x_input))

        # 2. Get values at that index
        t = self.times[idx]
        ang = self.angles[idx]
        cx = self.x_coords[idx]
        cy = self.y_coords[idx]

        # 3. Update Angle Graph Dot (Red Dot)
        if self.cursor_angle_dot:
            self.cursor_angle_dot.set_data([t], [ang])
        else:
            # Create the dot, setting zorder to ensure it is visible over the line
            self.cursor_angle_dot, = self.ax_angle.plot(t, ang, 'ro', markersize=6, zorder=5)

        # 4. Update CoP Graph Dot (Red Dot)
        if self.cursor_cop_dot:
            self.cursor_cop_dot.set_data([cx], [cy])
        else:
            self.cursor_cop_dot, = self.ax_cop.plot(cx, cy, 'ro', markersize=8, zorder=5)

        # 5. Efficient redraw
        self.canvas.draw_idle()

    def on_click(self, event):
        """Matplotlib event: Initiates the dragging state if the click occurs on the angle plot."""
        if event.inaxes == self.ax_angle:
            self.is_dragging = True
            self.update_cursors(event.xdata)

    def on_drag(self, event):
        """Matplotlib event: Updates the cursor position continuously while the mouse is dragged over the angle plot."""
        if self.is_dragging and event.inaxes == self.ax_angle:
            self.update_cursors(event.xdata)

    def on_release(self, event):
        """Matplotlib event: Terminates the dragging state."""
        self.is_dragging = False