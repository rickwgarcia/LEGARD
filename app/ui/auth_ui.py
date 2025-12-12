import tkinter as tk
from tkinter import messagebox, ttk
from core import auth_manager

# ---------------------
# File: auth_ui.py
# Author: Ricardo Garcia, ricardo.garcia@cosmiac.org
# Last Modified: 2025-12-12
# Version: 2.0.0
# ---------------------

"""
Module containing the user interface elements for the application's authentication flow.

It includes the main LoginApp window and the RegistrationWindow Toplevel window, 
handling user input, validation, and interaction with the auth_manager logic.
"""

class RegistrationWindow(tk.Toplevel):
    """
    A Toplevel window for new user registration.

    This window requires the user to input personal details, a username, and a 
    4-digit PIN. It validates the input and calls the authentication manager 
    to create the new account.
    """
    def __init__(self, parent):
        """
        Initializes the registration window.

        Args:
            parent (tk.Tk or tk.Toplevel): The parent window (usually the LoginApp).
        """
        super().__init__(parent)
        self.title("Register New User")
        self.attributes('-fullscreen', True)
        self.bind('<Escape>', lambda e: self.destroy())

        # UI Setup
        bg_frame = ttk.Frame(self)
        bg_frame.pack(fill="both", expand=True)

        frame = ttk.Frame(bg_frame, padding="20", relief="ridge", borderwidth=2)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        header = ttk.Label(frame, text="Create Account", font=("Helvetica", 16, "bold"))
        header.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        ttk.Label(frame, text="First Name:").grid(row=1, column=0, sticky="w", pady=5)
        self.first_name_entry = ttk.Entry(frame)
        self.first_name_entry.grid(row=1, column=1, sticky="ew", pady=5)

        ttk.Label(frame, text="Last Name:").grid(row=2, column=0, sticky="w", pady=5)
        self.last_name_entry = ttk.Entry(frame)
        self.last_name_entry.grid(row=2, column=1, sticky="ew", pady=5)

        ttk.Label(frame, text="Gender:").grid(row=3, column=0, sticky="w", pady=5)
        self.gender_combobox = ttk.Combobox(frame, values=["Male", "Female", "Other", "Prefer not to say"])
        self.gender_combobox.grid(row=3, column=1, sticky="ew", pady=5)

        ttk.Label(frame, text="Username:").grid(row=4, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(frame)
        self.username_entry.grid(row=4, column=1, sticky="ew", pady=5)

        ttk.Label(frame, text="Create 4-Digit PIN:").grid(row=5, column=0, sticky="w", pady=5)
        vcmd = (self.register(self.validate_pin), '%P')
        self.pin_entry = ttk.Entry(frame, show="*", validate="key", validatecommand=vcmd)
        self.pin_entry.grid(row=5, column=1, sticky="ew", pady=5)

        submit_button = ttk.Button(frame, text="Submit Registration", command=self.submit)
        submit_button.grid(row=6, column=0, columnspan=2, pady=(20, 5), sticky="ew")
        
        cancel_button = ttk.Button(frame, text="Cancel", command=self.destroy)
        cancel_button.grid(row=7, column=0, columnspan=2, pady=5, sticky="ew")

        frame.columnconfigure(1, weight=1)

    def validate_pin(self, new_value):
        """
        Tkinter validation command to ensure the PIN field accepts only digits 
        and is limited to a maximum length of 4 characters.

        Args:
            new_value (str): The value the entry field would have if the current 
                             keystroke were accepted.

        Returns:
            bool: True if the input is valid, False otherwise.
        """
        return (new_value == "" or new_value.isdigit()) and len(new_value) <= 4

    def submit(self):
        """
        Handles the submission of the registration form.

        Gathers data from entry fields, performs local PIN validation, and 
        calls `auth_manager.register_user` to create the account. Displays 
        success or error messages using Tkinter's messagebox.
        """
        pin = self.pin_entry.get()
        if len(pin) != 4:
            messagebox.showerror("Error", "Your PIN must be exactly 4 digits.")
            return
        
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        gender = self.gender_combobox.get()
        username = self.username_entry.get()

        # Call the Manager for logic
        success, message = auth_manager.register_user(username, pin, first_name, last_name, gender)
        
        if success:
            messagebox.showinfo("Success", message)
            self.destroy()
        else:
            messagebox.showerror("Error", message)

class LoginApp(tk.Tk):
    """
    The main Tkinter application window for user login.

    It collects username and PIN, handles the login process by interacting 
    with the auth_manager, and provides an option to open the registration window.
    """
    def __init__(self):
        """Initializes the main application window (Login screen)."""
        super().__init__()
        self.title("Exercise App Login")
        self.attributes('-fullscreen', True)
        self.bind('<Escape>', lambda e: self.destroy())
        
        main_frame = tk.Frame(self)
        main_frame.pack(expand=True)
        main_frame.columnconfigure(1, weight=1)
        
        ttk.Label(main_frame, text="Username:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.username_entry = ttk.Entry(main_frame)
        self.username_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(main_frame, text="Enter PIN:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.pin_entry = ttk.Entry(main_frame, show="*")
        self.pin_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Login", command=self.handle_login).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Register", command=self.handle_register).pack(side=tk.LEFT, padx=5)

    def handle_login(self):
        """
        Processes the login attempt.

        Gathers credentials and calls `auth_manager.login_user`. If successful, 
        it closes the login window and starts the main dashboard application. 
        If unsuccessful, it displays an error message.
        """
        username = self.username_entry.get()
        pin = self.pin_entry.get()
        
        # Call the Manager for logic
        success, message, full_name, gender = auth_manager.login_user(username, pin)
        
        if success:
            self.destroy()
            # Lazy import to avoid circular dependency
            from ui.dashboard import Dashboard
            dashboard = Dashboard(username, full_name, gender)
            dashboard.mainloop()
        else:
            messagebox.showerror("Login Failed", message)

    def handle_register(self):
        """Opens the RegistrationWindow as a Toplevel window."""
        RegistrationWindow(self)