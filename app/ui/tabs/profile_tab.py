import tkinter as tk
from tkinter import ttk

class ProfileTab(ttk.Frame):
    def __init__(self, parent, username, full_name, gender):
        super().__init__(parent)
        
        # Store user data
        self.username = username
        self.full_name = full_name
        self.gender = gender
        
        self._create_ui()

    def _create_ui(self):
        # Header
        ttk.Label(self, text=f"Welcome, {self.full_name}!", font=("Helvetica", 16)).pack(pady=20)
        
        # Info Container
        info_frame = ttk.Frame(self)
        info_frame.pack()
        
        # Username Row
        ttk.Label(info_frame, text="Username:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(info_frame, text=self.username).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        # Gender Row
        ttk.Label(info_frame, text="Gender:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(info_frame, text=self.gender).grid(row=1, column=1, sticky="w", padx=5, pady=2)