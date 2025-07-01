# legard_app/gui/login_frame.py

import tkinter as tk
from tkinter import ttk, font
from data.user_manager import UserManager

class LoginFrame(tk.Frame):
    """Frame for user login and registration."""
    def __init__(self, parent, on_login_success):
        super().__init__(parent, bg='white')
        self.on_login_success = on_login_success
        self.user_manager = UserManager()
        self.parent = parent
        
        # --- State Variables ---
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.reg_fname_var = tk.StringVar()
        self.reg_lname_var = tk.StringVar()
        self.reg_user_var = tk.StringVar()
        self.reg_pass_var = tk.StringVar()
        self.gender_var = tk.StringVar()

        # --- Fonts ---
        self.title_font = font.Font(family='Malgun', size=15, weight='bold')
        self.header_font = font.Font(family='Helvetica', size=12, weight='bold')
        self.label_font = font.Font(family='Helvetica', size=12, weight='bold')
        self.entry_font = font.Font(family='Helvetica', size=12)
        
        self._create_widgets()
        self._show_login_view() # Start with the login view

    def _create_widgets(self):
        # --- Main Layout ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        main_
