# gui/tabs/analytics_tab.py
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class AnalyticsTab:
    def __init__(self, parent, df):
        self.frame = tk.Frame(parent)
        self.df = df
        self.setup_ui()
    
    def setup_ui(self):
        # Repetitions per Day
        fig1 = Figure(figsize=(5, 2))
        canvas1 = FigureCanvasTkAgg(fig1, self.frame)
        canvas1.get_tk_widget().grid(row=0, column=0, pady=10)
        ax1 = fig1.add_subplot(111)
        ax1.set_ylabel('Repetitions')
        ax1.set_title('Repetitions per Day')
        if not self.df.empty:
            ax1.plot(self.df["Day"], self.df["Value"].apply(lambda x: x[0]))
        else:
            ax1.text(0.5, 0.5, 'No Data', horizontalalignment='center', verticalalignment='center')
        
        # Session Length
        fig2 = Figure(figsize=(5, 2))
        canvas2 = FigureCanvasTkAgg(fig2, self.frame)
        canvas2.get_tk_widget().grid(row=0, column=1, pady=10)
        ax2 = fig2.add_subplot(111)
        ax2.set_ylabel('Usage Time')
        ax2.set_title('Session Length')
        if not self.df.empty:
            ax2.bar(self.df["Day"], self.df["Value"].apply(lambda x: x[1]))
        else:
            ax2.text(0.5, 0.5, 'No Data', horizontalalignment='center', verticalalignment='center')
        
        # Resting Time Per Session
        fig3 = Figure(figsize=(5, 2))
        canvas3 = FigureCanvasTkAgg(fig3, self.frame)
        canvas3.get_tk_widget().grid(row=1, column=1)
        ax3 = fig3.add_subplot(111)
        ax3.set_ylabel('Resting Time')
        ax3.set_title('Resting Time Per Session')
        if not self.df.empty:
            ax3.bar(self.df["Day"], self.df["Value"].apply(lambda x: x[2]))
        else:
            ax3.text(0.5, 0.5, 'No Data', horizontalalignment='center', verticalalignment='center')

