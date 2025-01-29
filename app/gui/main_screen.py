# gui/main_screen.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from hardware.gpio_interface import GPIOInterface
from hardware.sensor_interface import SensorInterface
from utils.data_handler import DataHandler
from gui.tabs.user_info_tab import UserInfoTab
from gui.tabs.start_routine_tab import StartRoutineTab
from gui.tabs.check_history_tab import CheckHistoryTab
from gui.tabs.analytics_tab import AnalyticsTab

class MainScreen:
    def __init__(self, master, username):
        self.master = master
        self.username = username
        self.master.title('LEGARD Application - Main Screen')
        self.master.geometry(f"{master.winfo_screenwidth()}x{master.winfo_screenheight()}")
        
        # Initialize Hardware Interfaces
        self.gpio = GPIOInterface()
        self.sensor = SensorInterface(address=0x28)  # Adjust address if needed
        
        # Load User Data
        self.user, self.df, self.day = DataHandler.load_user_info(self.username)
        
        # Initialize Notebook (Tabs)
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=1, fill="both")
        
        # Initialize Tabs
        self.user_info_tab = UserInfoTab(self.notebook, self.user, self.df)
        self.start_routine_tab = StartRoutineTab(self.notebook, self.gpio, self.sensor, self.username, self.day)
        self.check_history_tab = CheckHistoryTab(self.notebook, self.username)
        self.analytics_tab = AnalyticsTab(self.notebook, self.df)
        
        # Add Tabs to Notebook
        self.notebook.add(self.user_info_tab.frame, text='User Info')
        self.notebook.add(self.start_routine_tab.frame, text='Start Routine')
        self.notebook.add(self.check_history_tab.frame, text='Check History')
        self.notebook.add(self.analytics_tab.frame, text='Analytics')
    
    def on_close(self):
        # Cleanup GPIO on close
        self.gpio.cleanup()
        self.master.destroy()

