# gui/login.py
import tkinter as tk
from tkinter import messagebox
import os

class LoginWindow:
    def __init__(self, master, on_success):
        self.master = master
        self.on_success = on_success
        self.setup_ui()
    
    def setup_ui(self):
        self.master.geometry(f"{self.master.winfo_screenwidth()}x{self.master.winfo_screenheight()}")
        self.master['bg'] = 'white'
        self.master.title('Log In')
        
        self.query = tk.StringVar()
        
        # Login Components
        tk.Label(self.master, text="User: ", font='Helvetica 15 bold', bg='white').grid(row=2, column=0, pady=30)
        self.user_box = tk.Entry(self.master, font='Helvetica 15', textvariable=self.query)
        self.user_box.grid(row=2, column=1)
        
        tk.Label(self.master, text="Password: ", font='Helvetica 15 bold', bg='white').grid(row=3, column=0)
        self.pass_box = tk.Entry(self.master, font='Helvetica 15', show="*")
        self.pass_box.grid(row=3, column=1)
        
        self.login_status = tk.Label(self.master, text="", font='Helvetica 10 bold', bg='white')
        self.login_status.grid(row=4, columnspan=4)
        
        login_button = tk.Button(self.master, text="Log In", bg='SpringGreen3', fg='black', font='Helvetica 10 bold', command=self.login)
        login_button.grid(row=5, column=1, ipadx=10, ipady=6, padx=30)
        
        # Registration Components
        tk.Button(self.master, text="Register", bg='brown2', fg='black', font='Helvetica 12 bold', command=self.show_register).grid(row=6, columnspan=4, sticky='ew', ipady=20)
    
    def login(self):
        username = self.user_box.get().strip()
        password = self.pass_box.get().strip()
        credentials = self.load_credentials()
        
        if username in credentials and credentials[username] == password:
            messagebox.showinfo("Success", f"Welcome {username}!")
            self.on_success(username)
        else:
            self.login_status.config(text="Credentials Not Found", fg='red')
    
    def load_credentials(self):
        credentials = {}
        register_file = os.path.join("Users", "register.txt")
        if os.path.exists(register_file):
            with open(register_file, "r") as file:
                for line in file:
                    user, pwd = line.strip().split('\t')
                    credentials[user] = pwd
        return credentials
    
    def show_register(self):
        self.master.withdraw()
        import gui.register as register_module
        register_window = tk.Toplevel(self.master)
        RegisterWindow(register_window, self.master)

