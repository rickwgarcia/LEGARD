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
        
        main_container = tk.Frame(self, bg='white')
        main_container.grid(row=1, column=0, sticky='ew')
        
        # --- Title and View Toggles ---
        tk.Label(main_container, text="Welcome to LEGARD!", font=self.title_font, bg='white').pack(fill='x', ipady=20)
        tk.Button(main_container, text="Log In", bg='grey82', font=self.header_font, width=90, command=self._show_login_view).pack(fill='x', ipady=10)

        # --- Login View Frame ---
        self.login_frame = tk.Frame(main_container, bg='white')
        self._create_login_widgets(self.login_frame)
        
        tk.Button(main_container, text="Register", bg='brown2', font=self.header_font, command=self._show_register_view).pack(fill='x', ipady=10, pady=(20,0))
        
        # --- Registration View Frame ---
        self.register_frame = tk.Frame(main_container, bg='white')
        self._create_register_widgets(self.register_frame)
        
        # --- Message/Status Label ---
        self.message_label = tk.Label(main_container, text="", font=self.label_font, bg='white', fg='red')
        self.message_label.pack(pady=20)

    def _create_login_widgets(self, parent):
        form_frame = tk.Frame(parent, bg='white')
        form_frame.pack(pady=20)
        tk.Label(form_frame, text="User:", font=self.label_font, bg='white').grid(row=0, column=0, sticky='e', padx=5, pady=10)
        tk.Entry(form_frame, textvariable=self.username_var, font=self.entry_font).grid(row=0, column=1, padx=5, pady=10)
        tk.Label(form_frame, text="Password:", font=self.label_font, bg='white').grid(row=1, column=0, sticky='e', padx=5, pady=10)
        tk.Entry(form_frame, textvariable=self.password_var, show="*", font=self.entry_font).grid(row=1, column=1, padx=5, pady=10)
        tk.Button(parent, text="Log In", bg='SpringGreen3', font=self.header_font, command=self._handle_login).pack(ipadx=10, ipady=6)

    def _create_register_widgets(self, parent):
        form_frame = tk.Frame(parent, bg='white')
        form_frame.pack(pady=20)
        
        # FName, LName
        tk.Label(form_frame, text="First Name:", font=self.label_font, bg='white').grid(row=0, column=0, sticky='e', padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.reg_fname_var, font=self.entry_font).grid(row=0, column=1, sticky='w', padx=5, pady=5)
        tk.Label(form_frame, text="Last Name:", font=self.label_font, bg='white').grid(row=0, column=2, sticky='e', padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.reg_lname_var, font=self.entry_font).grid(row=0, column=3, sticky='w', padx=5, pady=5)

        # Gender
        tk.Label(form_frame, text="Gender:", font=self.label_font, bg='white').grid(row=1, column=0, sticky='e', padx=5, pady=5)
        gender_frame = tk.Frame(form_frame, bg='white')
        tk.Radiobutton(gender_frame, text="Male", variable=self.gender_var, value="Male", bg='white', font=self.entry_font).pack(side='left')
        tk.Radiobutton(gender_frame, text="Female", variable=self.gender_var, value="Female", bg='white', font=self.entry_font).pack(side='left')
        gender_frame.grid(row=1, column=1, columnspan=3, sticky='w')

        # User, Pass
        tk.Label(form_frame, text="Username:", font=self.label_font, bg='white').grid(row=2, column=0, sticky='e', padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.reg_user_var, font=self.entry_font).grid(row=2, column=1, sticky='w', padx=5, pady=5)
        tk.Label(form_frame, text="Password:", font=self.label_font, bg='white').grid(row=2, column=2, sticky='e', padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.reg_pass_var, show="*", font=self.entry_font).grid(row=2, column=3, sticky='w', padx=5, pady=5)
        
        tk.Button(parent, text="Register", bg='SpringGreen3', font=self.header_font, command=self._handle_register).pack(ipadx=10, ipady=6, pady=10)
    
    def _show_login_view(self):
        self.register_frame.pack_forget()
        self.login_frame.pack()
        self.message_label.config(text="")

    def _show_register_view(self):
        self.login_frame.pack_forget()
        self.register_frame.pack()
        self.message_label.config(text="")

    def _handle_login(self):
        username = self.username_var.get()
        password = self.password_var.get()
        if self.user_manager.login(username, password):
            self.message_label.config(text=f"Welcome {username}", fg='green')
            self.on_login_success(self.user_manager)
        else:
            self.message_label.config(text="Credentials not found", fg='red')
            
    def _handle_register(self):
        result = self.user_manager.register(
            first=self.reg_fname_var.get(),
            last=self.reg_lname_var.get(),
            gender=self.gender_var.get(),
            username=self.reg_user_var.get(),
            password=self.reg_pass_var.get()
        )
        if result == "success":
            self.message_label.config(text="Registration successful! Please log in.", fg='green')
            self._show_login_view()
        elif result == "user_exists":
            self.message_label.config(text="Username already exists.", fg='red')
        elif result == "empty_credentials":
            self.message_label.config(text="Username and password cannot be empty.", fg='red')