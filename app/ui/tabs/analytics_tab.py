import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import csv
import glob
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from core.config_manager import config

# ---------------------
# File: analytics_tab.py
# Author: Ricardo Garcia, ricardo.garcia@cosmiac.org
# Last Modified: 2025-12-12
# Version: 2.0.0
# ---------------------

"""
Module containing the AnalyticsTab, a Tkinter frame responsible for 
parsing user session data from CSV files and visualizing it using Matplotlib.
"""

class AnalyticsTab(ttk.Frame):
    """
    A Tkinter tab within the main dashboard that provides data visualization 
    and analysis of a user's exercise history.

    It reads session data from the user's directory, aggregates statistics, 
    and displays various performance graphs.
    """
    def __init__(self, parent, username):
        """
        Initializes the AnalyticsTab.

        Args:
            parent (ttk.Notebook): The Notebook widget this tab belongs to.
            username (str): The username of the currently logged-in user.
        """
        super().__init__(parent)
        self.username = username
        self.sessions_dir = config.get('Paths', 'sessions_base_dir')
        self.user_dir = os.path.join(self.sessions_dir, self.username)
        
        # Data containers
        self.session_data = [] # List of dicts containing parsed stats per session
        # self.daily_reps = defaultdict(int) # REMOVED: No longer needed for 'reps per day'
        self.weekly_sessions = defaultdict(int) # Aggregates session count by week key (YYYY-WNN)
        self.monthly_sessions = defaultdict(int) # Aggregates session count by month key (YYYY-MM)

        self.graph_options = [
            "Select a Graph...",
            "Repetitions per Session", # MODIFIED
            "Sessions per Week",
            "Avg Velocity per Session",
            "Avg Max Angle per Session",
            "Target Angle per Session"
        ]

        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        """Sets up the Tkinter layout, including the graph selector and Matplotlib canvas."""
        # Top control bar
        control_frame = ttk.Frame(self)
        control_frame.pack(fill='x', pady=5, padx=5)
        
        # Refresh Button
        ttk.Button(control_frame, text="Refresh Data", command=self.refresh_data).pack(side='right')
        
        # Dropdown Menu
        ttk.Label(control_frame, text="View: ").pack(side='left', padx=(0, 5))
        
        self.graph_selector = ttk.Combobox(
            control_frame, 
            values=self.graph_options, 
            state="readonly", 
            width=30
        )
        self.graph_selector.current(0)
        self.graph_selector.pack(side='left')
        
        self.graph_selector.bind("<<ComboboxSelected>>", self.on_graph_select)

        # Graphs Container
        self.graph_frame = ttk.Frame(self)
        self.graph_frame.pack(fill='both', expand=True)

        # Initialize Matplotlib Figure and link to Tkinter
        self.fig = plt.Figure(figsize=(10, 8), dpi=100)
        self.ax1 = self.fig.add_subplot(111) 
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Initial blank state
        self.ax1.axis('off')

    def refresh_data(self):
        """Parses the raw data files and redraws the currently selected graph."""
        self.parse_history()
        self.plot_graphs()

    def on_graph_select(self, event):
        """Event handler for the graph selector combobox; triggers graph redraw."""
        self.plot_graphs()

    def parse_history(self):
        """
        Reads all CSV data files for the current user, extracts metadata and 
        performance statistics, and aggregates them into instance variables.

        Calculates:
        - Session count per week and month.
        - Per-session averages for velocity and max angle achieved per rep.
        - Total reps per session (which is used for the Reps per Session plot).
        """
        # Reset containers
        # self.daily_reps.clear() # REMOVED
        self.weekly_sessions.clear()
        self.monthly_sessions.clear()
        self.session_data = []

        if not os.path.exists(self.user_dir):
            return

        files = glob.glob(os.path.join(self.user_dir, "*.csv"))
        # Sort by filename (which contains date) to ensure chronological order
        files.sort() 

        for filepath in files:
            filename = os.path.basename(filepath)
            try:
                # Filename format: datalog_YYYYMMDD_HHMMSS.csv
                parts = filename.split('_')
                date_part = parts[1]
                time_part = parts[2].split('.')[0]
                session_dt = datetime.strptime(f"{date_part}{time_part}", "%Y%m%d%H%M%S")
                display_date = session_dt.strftime("%Y-%m-%d")
                
                # Keys for frequency charts
                week_key = session_dt.strftime("%Y-W%U")
                month_key = session_dt.strftime("%Y-%m")
                
            except (IndexError, ValueError):
                continue 

            # Per Session Variables
            target_angle = 0.0
            max_angle_calibration = 0.0
            
            rep_max_angles = defaultdict(float) 
            positive_velocities = []
            set_max_reps = defaultdict(int)

            try:
                with open(filepath, 'r') as f:
                    reader = csv.reader(f)
                    
                    # Parse Metadata Rows
                    row1 = next(reader, None)
                    if row1 and row1[0] == 'Max':
                        max_angle_calibration = float(row1[1])
                    
                    row2 = next(reader, None)
                    if row2 and row2[0] == 'Target':
                        target_angle = float(row2[1])

                    headers = next(reader, None) # Skip Headers
                    
                    # Parse Data Rows
                    for row in reader:
                        if len(row) < 5: continue
                        try:
                            set_num = int(row[0])
                            rep_count = int(row[2])
                            angle = float(row[3])
                            velocity = float(row[4])

                            # Track Max Reps per Set
                            if rep_count > set_max_reps[set_num]:
                                set_max_reps[set_num] = rep_count

                            # Track Max Angle per specific Rep
                            key = (set_num, rep_count)
                            if angle > rep_max_angles[key]:
                                rep_max_angles[key] = angle

                            # Track Positive Velocity
                            if velocity > 0:
                                positive_velocities.append(velocity)

                        except ValueError:
                            continue
                    
                    # Session Aggregation
                    total_reps = sum(set_max_reps.values())
                    # self.daily_reps[display_date] += total_reps # REMOVED
                    
                    self.weekly_sessions[week_key] += 1
                    self.monthly_sessions[month_key] += 1

                    # Calculate Averages
                    avg_velocity = 0.0
                    if positive_velocities:
                        avg_velocity = sum(positive_velocities) / len(positive_velocities)
                    
                    avg_max_angle = 0.0
                    if rep_max_angles:
                        avg_max_angle = sum(rep_max_angles.values()) / len(rep_max_angles)

                    self.session_data.append({
                        'dt': session_dt,
                        'date_str': display_date,
                        'target_angle': target_angle,
                        'avg_pos_velocity': avg_velocity,
                        'avg_max_angle': avg_max_angle,
                        'total_reps': total_reps # This is the reps per session
                    })

            except Exception as e:
                print(f"Error parsing {filename}: {e}")

    def plot_graphs(self):
        """Clears the existing Matplotlib figure and draws the graph based on the current selection."""
        self.ax1.clear()
        self.ax1.axis('on')
        selection = self.graph_selector.get()

        if selection == "Repetitions per Session": # MODIFIED
            self.draw_reps_per_session() # MODIFIED
        elif selection == "Sessions per Week":
            self.draw_sessions_per_week()
        elif selection == "Avg Velocity per Session":
            self.draw_line_plot_over_time("avg_pos_velocity", "Velocity (deg/s)", "Avg Velocity per Session")
        elif selection == "Avg Max Angle per Session":
            self.draw_line_plot_over_time("avg_max_angle", "Angle (degrees)", "Avg Max Angle per Session")
        elif selection == "Target Angle per Session":
            self.draw_line_plot_over_time("target_angle", "Angle (degrees)", "Target Angle per Session")
        else:
            self.ax1.axis('off')
            self.ax1.text(0.5, 0.5, "Select a graph to view analytics", ha='center')

        self.fig.tight_layout()
        self.canvas.draw()

    def draw_reps_per_session(self):
        """Draws a line plot showing the total number of repetitions completed in each session."""
        if not self.session_data:
            self.ax1.text(0.5, 0.5, "No Data", ha='center'); return

        # This now uses the same plotting logic as other session-based plots
        self.draw_line_plot_over_time("total_reps", "Total Repetitions", "Repetitions per Session")

    def draw_sessions_per_week(self):
        """Draws a line plot showing the number of sessions completed per week to match the style."""
        if not self.weekly_sessions:
            self.ax1.text(0.5, 0.5, "No Data", ha='center'); return
        
        weeks = sorted(self.weekly_sessions.keys())
        counts = [self.weekly_sessions[w] for w in weeks]
        
        # Changed from bar chart to line plot
        self.ax1.plot(weeks, counts, marker='o', linestyle='-', color='royalblue', linewidth=2)
        
        self.ax1.set_title("Sessions per Week", fontsize=14)
        self.ax1.set_ylabel("Count", fontsize=12)
        self.ax1.set_xlabel("Week (Year-Week)", fontsize=12)
        self.ax1.grid(True, linestyle='--', alpha=0.7) # Added grid for consistency
        self.ax1.tick_params(axis='x', rotation=45)

        self.ax1.yaxis.get_major_locator().set_params(integer=True)

    def draw_line_plot_over_time(self, key, y_label, title):
        """
        Draws a line plot showing a specific metric over the chronological sequence of sessions.

        Args:
            key (str): The key in `self.session_data` dictionary to plot (e.g., 'avg_pos_velocity').
            y_label (str): The label for the Y-axis.
            title (str): The title for the graph.
        """
        if not self.session_data:
            self.ax1.text(0.5, 0.5, "No Data", ha='center'); return

        values = [s[key] for s in self.session_data]
        session_indices = range(1, len(values) + 1)

        self.ax1.plot(session_indices, values, marker='o', linestyle='-', color='royalblue', linewidth=2)
        
        self.ax1.set_title(title, fontsize=14)
        self.ax1.set_ylabel(y_label, fontsize=12)
        self.ax1.set_xlabel("Session Number", fontsize=12)
        self.ax1.grid(True, linestyle='--', alpha=0.7)
        
        self.ax1.xaxis.get_major_locator().set_params(integer=True)