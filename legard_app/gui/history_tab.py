# legard_app/gui/history_tab.py

import tkinter as tk
from tkinter import ttk
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class HistoryTab(tk.Frame):
    """The 'Check History' tab view."""
    def __init__(self, parent, user_manager):
        super().__init__(parent)
        self.user_manager = user_manager
        self.session_files = self.user_manager.get_session_files()
        
        self._create_widgets()

    def _create_widgets(self):
        # --- File Selection Dropdown ---
        self.clicked_file = tk.StringVar(self)
        if self.session_files:
            self.clicked_file.set(self.session_files[0]) # Default value
            drop = ttk.OptionMenu(self, self.clicked_file, self.session_files[0], *self.session_files)
        else:
            self.clicked_file.set("No sessions found")
            drop = ttk.OptionMenu(self, self.clicked_file, "No sessions found")
        drop.pack(pady=5)

        ttk.Button(self, text="View Session", command=self._show_session_data).pack(pady=5)
        self.message_label = ttk.Label(self, text="")
        self.message_label.pack(pady=5)

        # --- Matplotlib Figure and Canvas ---
        self.fig = plt.Figure(figsize=(12, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(pady=10)
        
        # Two sub-plots: line plot and heatmap
        self.line_plot_ax = self.fig.add_subplot(1, 2, 1)
        self.heatmap_ax = self.fig.add_subplot(1, 2, 2)
        self.fig.subplots_adjust(bottom=0.1, wspace=0.3)

    def _show_session_data(self):
        """Parses and displays data for the selected session file."""
        filename = self.clicked_file.get()
        if not filename or filename == "No sessions found":
            self.message_label.config(text="Please select a session file.")
            return

        filepath = os.path.join(self.user_manager.USERS_DIR, self.user_manager.username, filename)
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()

            # Simple parsing logic (can be made more robust)
            parts = content.split('X(Time)\tY(Sensor 1 Angle)\tY(Sensor 2 Angle)')
            if len(parts) != 2:
                raise ValueError("Unsupported file format")

            time_series_data = parts[1].strip().split('\n')
            
            X, Y1, Y2 = [], [], []
            for line in time_series_data:
                cols = line.split('\t')
                if len(cols) >= 3:
                    X.append(float(cols[0]))
                    Y1.append(float(cols[1]))
                    Y2.append(float(cols[2]))

            self._update_plots(X, Y1, Y2)
            self.message_label.config(text=f"Viewing: {filename}")

        except Exception as e:
            self.message_label.config(text=f"Error reading file: {e}")
            self._clear_plots()

    def _update_plots(self, X, Y1, Y2):
        self.line_plot_ax.clear()
        self.heatmap_ax.clear()

        # Line plot
        self.line_plot_ax.plot(X, Y1, label='Sensor 1 Angle')
        self.line_plot_ax.plot(X, Y2, label='Sensor 2 Angle', linestyle='--')
        self.line_plot_ax.set_title("Angle Over Time")
        self.line_plot_ax.set_xlabel("Time (s)")
        self.line_plot_ax.set_ylabel("Relative Angle (°)")
        self.line_plot_ax.legend()
        self.line_plot_ax.grid(True)
        
        # Heatmap (if data exists)
        # The original code had a section for "X Cord, Y Cord" which we can add here if needed.
        # For now, we'll leave it blank.
        self.heatmap_ax.set_title("Cartesian Heat-Map (Not Implemented)")
        self.heatmap_ax.text(0.5, 0.5, "No Cartesian data in this file", ha='center', va='center')

        self.canvas.draw()
        
    def _clear_plots(self):
        self.line_plot_ax.clear()
        self.heatmap_ax.clear()
        self.line_plot_ax.set_title("Angle Over Time")
        self.heatmap_ax.set_title("Cartesian Heat-Map")
        self.canvas.draw()
