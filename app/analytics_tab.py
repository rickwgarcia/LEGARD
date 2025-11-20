import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import csv
import glob
from datetime import datetime
from collections import defaultdict
from config_manager import config

class AnalyticsTab(ttk.Frame):
    def __init__(self, parent, username):
        super().__init__(parent)
        self.username = username
        self.sessions_dir = config.get('Paths', 'sessions_base_dir')
        self.user_dir = os.path.join(self.sessions_dir, self.username)
        
        # Data containers
        self.daily_reps = defaultdict(int)

        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        # Top control bar
        control_frame = ttk.Frame(self)
        control_frame.pack(fill='x', pady=5, padx=5)
        
        ttk.Button(control_frame, text="Refresh Data", command=self.refresh_data).pack(side='right')
        ttk.Label(control_frame, text="Daily Repetitions", font=("Helvetica", 16, "bold")).pack(side='left')

        # Graphs Container
        self.graph_frame = ttk.Frame(self)
        self.graph_frame.pack(fill='both', expand=True)

        # Initialize Matplotlib Figure
        self.fig = plt.Figure(figsize=(10, 8), dpi=100)
        self.ax1 = self.fig.add_subplot(111) 

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def refresh_data(self):
        """Reads all CSV files and recalculates metrics."""
        self.parse_history()
        self.plot_graphs()

    def parse_history(self):
        self.daily_reps.clear()

        if not os.path.exists(self.user_dir):
            return

        # Get all CSV files
        files = glob.glob(os.path.join(self.user_dir, "*.csv"))
        files.sort() # Process in chronological order

        for filepath in files:
            filename = os.path.basename(filepath)
            try:
                date_part = filename.split('_')[1]
                session_datetime = datetime.strptime(date_part, "%Y%m%d")
                display_date = session_datetime.strftime("%Y-%m-%d")
            except IndexError:
                continue 

            set_max_reps = {}

            try:
                with open(filepath, 'r') as f:
                    reader = csv.reader(f)
                    next(reader, None) # Skip Header 1
                    next(reader, None) # Skip Header 2
                    
                    for row in reader:
                        if len(row) < 3: continue
                        
                        try:
                            set_num = int(row[0])
                            reps = int(row[2])

                            if set_num not in set_max_reps:
                                set_max_reps[set_num] = 0
                            
                            if reps > set_max_reps[set_num]:
                                set_max_reps[set_num] = reps
                                
                        except ValueError:
                            continue
                    
                    total_reps_in_session = sum(set_max_reps.values())
                    self.daily_reps[display_date] += total_reps_in_session

            except Exception as e:
                print(f"Error parsing {filename}: {e}")

    def plot_graphs(self):
        # Clear axes
        self.ax1.clear()

        if self.daily_reps:
            sorted_dates = sorted(self.daily_reps.keys())
            reps = [self.daily_reps[d] for d in sorted_dates]
            
            # Create the bar chart
            bars = self.ax1.bar(sorted_dates, reps, color='skyblue', edgecolor='black')
            
            self.ax1.set_title("Total Repetitions per Day", fontsize=14)
            self.ax1.set_ylabel("Total Reps", fontsize=12)
            self.ax1.set_xlabel("Date", fontsize=12)
            
            self.ax1.tick_params(axis='x', rotation=45)
            self.ax1.grid(axis='y', linestyle='--', alpha=0.7)

            # --- Manual Labeling for compatibility with older Matplotlib versions ---
            for bar in bars:
                height = bar.get_height()
                self.ax1.text(
                    bar.get_x() + bar.get_width() / 2.,  # X position
                    height,                              # Y position
                    f'{int(height)}',                    # Text value
                    ha='center',                         # Horizontal alignment
                    va='bottom'                          # Vertical alignment
                )
            # ----------------------------------------------------------------------

        else:
            self.ax1.text(0.5, 0.5, "No Data Found", ha='center', fontsize=14)

        self.fig.tight_layout()
        self.canvas.draw()