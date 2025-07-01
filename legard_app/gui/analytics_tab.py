# legard_app/gui/analytics_tab.py

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AnalyticsTab(tk.Frame):
    """The 'Analytics' tab view for summary charts."""
    def __init__(self, parent, user_manager):
        super().__init__(parent)
        self.user_manager = user_manager
        self._create_widgets()
    
    def _create_widgets(self):
        df = self.user_manager.history_df
        days = df['Day']
        reps = [val[0] for val in df['Value']]
        usage_time = [val[1] for val in df['Value']]
        rest_time = [val[2] for val in df['Value']]
        
        fig = plt.Figure(figsize=(14, 6), dpi=100)
        
        # Repetitions Plot
        ax1 = fig.add_subplot(1, 3, 1)
        ax1.plot(days, reps, marker='o', linestyle='-')
        ax1.set_title('Repetitions per Day')
        ax1.set_ylabel('Repetitions')
        ax1.tick_params(axis='x', rotation=45)
        
        # Usage Time Plot
        ax2 = fig.add_subplot(1, 3, 2)
        ax2.bar(days, usage_time, color='skyblue')
        ax2.set_title('Session Length (s)')
        ax2.set_ylabel('Usage Time (s)')
        ax2.tick_params(axis='x', rotation=45)

        # Resting Time Plot
        ax3 = fig.add_subplot(1, 3, 3)
        ax3.bar(days, rest_time, color='lightgreen')
        ax3.set_title('Resting Time per Session (s)')
        ax3.set_ylabel('Resting Time (s)')
        ax3.tick_params(axis='x', rotation=45)

        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
