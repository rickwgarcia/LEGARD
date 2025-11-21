import tkinter as tk
from tkinter import messagebox, ttk
import auth_manager

class RegistrationWindow(tk.Toplevel):
    def __init__(self, parent):
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
        return (new_value == "" or new_value.isdigit()) and len(new_value) <= 4

    def submit(self):
        pin = self.pin_entry.get()
        if len(pin) != 4:
            messagebox.showerror("Error", "Your PIN must be exactly 4 digits.")
            return
        
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        gender = self.gender_combobox.get()
        username = self.username_entry.get()

        # Use the Manager for logic
        success, message = auth_manager.register_user(username, pin, first_name, last_name, gender)
        
        if success:
            messagebox.showinfo("Success", message)
            self.destroy()
        else:
            messagebox.showerror("Error", message)

class LoginApp(tk.Tk):
    def __init__(self):
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
        username = self.username_entry.get()
        pin = self.pin_entry.get()
        
        # Use the Manager for logic
        success, message, full_name, gender = auth_manager.login_user(username, pin)
        
        if success:
            self.destroy()
            # Lazy import to avoid circular dependency
            from dashboard import Dashboard
            dashboard = Dashboard(username, full_name, gender)
            dashboard.mainloop()
        else:
            messagebox.showerror("Login Failed", message)

    def handle_register(self):
        RegistrationWindow(self)