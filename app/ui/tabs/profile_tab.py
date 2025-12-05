import tkinter as tk
from tkinter import ttk

"""
Module containing the ProfileTab, a simple Tkinter frame used to display 
the currently logged-in user's profile information within the dashboard.
"""

class ProfileTab(ttk.Frame):
    """
    A read-only Tkinter tab component that presents the user's name, 
    username, and gender.
    """
    def __init__(self, parent, username, full_name, gender):
        """
        Initializes the ProfileTab and stores the user's details.

        Args:
            parent (ttk.Notebook): The Notebook widget this tab belongs to.
            username (str): The unique username of the user.
            full_name (str): The user's full name for display.
            gender (str): The user's registered gender.
        """
        super().__init__(parent)
        
        # Store user data
        self.username = username
        self.full_name = full_name
        self.gender = gender
        
        self._create_ui()

    def _create_ui(self):
        """Constructs the user interface elements using Tkinter widgets."""
        # Header displaying the full name
        ttk.Label(self, text=f"Welcome, {self.full_name}!", font=("Helvetica", 16)).pack(pady=20)
        
        # Info Container using grid for alignment
        info_frame = ttk.Frame(self)
        info_frame.pack()
        
        # Username Row
        ttk.Label(info_frame, text="Username:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(info_frame, text=self.username).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        # Gender Row
        ttk.Label(info_frame, text="Gender:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(info_frame, text=self.gender).grid(row=1, column=1, sticky="w", padx=5, pady=2)