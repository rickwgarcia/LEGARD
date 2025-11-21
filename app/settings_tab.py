import tkinter as tk
from tkinter import ttk, messagebox

class SettingsTab(tk.Frame):
    def __init__(self, parent, username):
        """
        Initialize the Settings Tab.
        
        :param parent: The parent widget (usually a frame or window).
        :param username: The username string passed from the main application.
        """
        super().__init__(parent)
        self.username = username
        
        # Configuration for the layout
        self.configure(bg="#f0f0f0") # Light gray background
        
        # Create the UI elements
        self.create_widgets()

    def create_widgets(self):
        """Creates and packs the labels and buttons."""
        
        # 1. Header / Welcome Label
        header_label = tk.Label(
            self, 
            text=f"Settings for {self.username}", 
            font=("Arial", 16, "bold"),
            bg="#f0f0f0"
        )
        header_label.pack(pady=20)

        # 2. Button 1: Change Password
        btn_password = ttk.Button(
            self, 
            text="Change Password", 
            command=self.change_password_action
        )
        btn_password.pack(pady=10, ipadx=10, ipady=5)

        # 3. Button 2: Toggle Theme
        btn_theme = ttk.Button(
            self, 
            text="Toggle Dark Mode", 
            command=self.toggle_theme_action
        )
        btn_theme.pack(pady=10, ipadx=10, ipady=5)

        # 4. Button 3: Logout
        btn_logout = ttk.Button(
            self, 
            text="Logout", 
            command=self.logout_action
        )
        btn_logout.pack(pady=10, ipadx=10, ipady=5)

    # --- Button Function Definitions ---

    def change_password_action(self):
        print(f"Action: Changing password for {self.username}...")
        # Placeholder for actual logic
        messagebox.showinfo("Settings", "Change Password clicked!")

    def toggle_theme_action(self):
        print("Action: Toggling theme...")
        # Placeholder for actual logic
        messagebox.showinfo("Settings", "Theme toggled!")

    def logout_action(self):
        print(f"Action: Logging out {self.username}...")
        # Placeholder for actual logic
        messagebox.showwarning("Settings", "Logout clicked!")