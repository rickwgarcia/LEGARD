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
from config_manager import config

class AnalyticsTab(ttk.Frame):
    def __init__(self, parent, username):
        super().__init__(parent)
        self.username = username
        self.sessions_dir = config.get('Paths', 'sessions_base_dir')
        self.user_dir = os.path.join(self.sessions_dir, self.username)
        
        # Data containers
        self.session_data = [] # List of dicts containing parsed stats per session
        self.daily_reps = defaultdict(int)
        self.weekly_sessions = defaultdict(int)
        self.monthly_sessions = defaultdict(int)

        # --- Updated Naming Convention ---
        self.graph_options = [
            "Select a Graph...",
            "Repetitions per Day",
            "Sessions per Week",
            "Avg Velocity per Session",
            "Avg Max Angle per Session",
            "Target Angle per Session"
        ]

        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        # --- Top control bar ---
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
        self.graph_selector.current(0) # Select default
        self.graph_selector.pack(side='left')
        
        self.graph_selector.bind("<<ComboboxSelected>>", self.on_graph_select)

        # --- Graphs Container ---
        self.graph_frame = ttk.Frame(self)
        self.graph_frame.pack(fill='both', expand=True)

        # Initialize Matplotlib Figure
        self.fig = plt.Figure(figsize=(10, 8), dpi=100)
        self.ax1 = self.fig.add_subplot(111) 
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Initial blank state
        self.ax1.axis('off')

    def refresh_data(self):
        self.parse_history()
        self.plot_graphs()

    def on_graph_select(self, event):
        self.plot_graphs()

    def parse_history(self):
        # Reset containers
        self.daily_reps.clear()
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
                week_key = session_dt.strftime("%Y-W%U") # Year-WeekNumber
                month_key = session_dt.strftime("%Y-%m")
                
            except (IndexError, ValueError):
                continue 

            # --- Per Session Variables ---
            target_angle = 0.0
            max_angle_calibration = 0.0
            
            # Rep tracking
            rep_max_angles = defaultdict(float) # Key: (set, rep_count), Value: max_angle
            
            # Velocity tracking
            positive_velocities = []
            
            # Total Reps (using the max rep count per set logic)
            set_max_reps = defaultdict(int)

            try:
                with open(filepath, 'r') as f:
                    reader = csv.reader(f)
                    
                    # -- Parse Metadata Rows --
                    # Row 1: Max Calibration
                    row1 = next(reader, None)
                    if row1 and row1[0] == 'Max':
                        max_angle_calibration = float(row1[1])
                    
                    # Row 2: Target Angle
                    row2 = next(reader, None)
                    if row2 and row2[0] == 'Target':
                        target_angle = float(row2[1])

                    # Row 3: Headers (Skip)
                    headers = next(reader, None)
                    
                    # -- Parse Data Rows --
                    for row in reader:
                        if len(row) < 5: continue
                        try:
                            set_num = int(row[0])
                            rep_count = int(row[2]) # This is "completed reps"
                            angle = float(row[3])
                            velocity = float(row[4])

                            # 1. Track Max Reps per Set
                            if rep_count > set_max_reps[set_num]:
                                set_max_reps[set_num] = rep_count

                            # 2. Track Max Angle per specific Rep
                            key = (set_num, rep_count)
                            if angle > rep_max_angles[key]:
                                rep_max_angles[key] = angle

                            # 3. Track Positive Velocity
                            if velocity > 0:
                                positive_velocities.append(velocity)

                        except ValueError:
                            continue
                    
                    # -- Session Aggregation --
                    total_reps = sum(set_max_reps.values())
                    self.daily_reps[display_date] += total_reps
                    
                    # Only count session if it had data
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
                        'total_reps': total_reps
                    })

            except Exception as e:
                print(f"Error parsing {filename}: {e}")

    def plot_graphs(self):
        self.ax1.clear()
        self.ax1.axis('on') # Default on
        selection = self.graph_selector.get()

        if selection == "Repetitions per Day":
            self.draw_daily_reps()
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

    def draw_daily_reps(self):
        if not self.daily_reps:
            self.ax1.text(0.5, 0.5, "No Data", ha='center'); return

        dates = sorted(self.daily_reps.keys())
        reps = [self.daily_reps[d] for d in dates]
        
        bars = self.ax1.bar(dates, reps, color='skyblue', edgecolor='black')
        self.ax1.set_title("Repetitions per Day")
        self.ax1.set_ylabel("Total Reps")
        self.ax1.tick_params(axis='x', rotation=45)
        
        for bar in bars:
            height = bar.get_height()
            self.ax1.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}', ha='center', va='bottom')

    def draw_sessions_per_week(self):
        if not self.weekly_sessions:
            self.ax1.text(0.5, 0.5, "No Data", ha='center'); return
        
        weeks = sorted(self.weekly_sessions.keys())
        counts = [self.weekly_sessions[w] for w in weeks]
        
        bars = self.ax1.bar(weeks, counts, color='lightgreen', edgecolor='black')
        self.ax1.set_title("Sessions per Week")
        self.ax1.set_ylabel("Count")
        self.ax1.set_xlabel("Week (Year-Week)")
        self.ax1.tick_params(axis='x', rotation=45)

        self.ax1.yaxis.get_major_locator().set_params(integer=True)

        for bar in bars:
            height = bar.get_height()
            self.ax1.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}', ha='center', va='bottom')

    def draw_line_plot_over_time(self, key, y_label, title):
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