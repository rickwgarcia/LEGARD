# gui/register.py
import tkinter as tk
from tkinter import messagebox
import os

class RegisterWindow:
    def __init__(self, master, login_master):
        self.master = master
        self.login_master = login_master
        self.setup_ui()
    
    def setup_ui(self):
        self.master.title("Register")
        self.master['bg'] = 'white'
        self.master.geometry("600x400")
        
        # First Name
        tk.Label(self.master, text="First Name: ", font='Helvetica 12 bold', bg='white').grid(row=0, column=0, pady=10, padx=10, sticky='e')
        self.fname_box = tk.Entry(self.master, width=20, font='Helvetica 12')
        self.fname_box.grid(row=0, column=1, pady=10, padx=10, sticky='w')
        
        # Last Name
        tk.Label(self.master, text="Last Name: ", font='Helvetica 12 bold', bg='white').grid(row=1, column=0, pady=10, padx=10, sticky='e')
        self.lname_box = tk.Entry(self.master, width=20, font='Helvetica 12')
        self.lname_box.grid(row=1, column=1, pady=10, padx=10, sticky='w')
        
        # Username
        tk.Label(self.master, text="Username: ", font='Helvetica 12 bold', bg='white').grid(row=2, column=0, pady=10, padx=10, sticky='e')
        self.user_box = tk.Entry(self.master, width=20, font='Helvetica 12')
        self.user_box.grid(row=2, column=1, pady=10, padx=10, sticky='w')
        
        # Password
        tk.Label(self.master, text="Password: ", font='Helvetica 12 bold', bg='white').grid(row=3, column=0, pady=10, padx=10, sticky='e')
        self.pass_box = tk.Entry(self.master, width=20, font='Helvetica 12', show="*")
        self.pass_box.grid(row=3, column=1, pady=10, padx=10, sticky='w')
        
        # Gender
        tk.Label(self.master, text="Gender: ", font='Helvetica 12 bold', bg='white').grid(row=4, column=0, pady=10, padx=10, sticky='e')
        self.gender_var = tk.StringVar(value="NotSelected")
        tk.Radiobutton(self.master, text="Male", variable=self.gender_var, value="Male", bg='white').grid(row=4, column=1, pady=10, padx=10, sticky='w')
        tk.Radiobutton(self.master, text="Female", variable=self.gender_var, value="Female", bg='white').grid(row=4, column=1, pady=10, padx=80, sticky='w')
        
        # Register Button
        register_button = tk.Button(self.master, text="Register", bg='SpringGreen3', fg='black', font='Helvetica 10 bold', command=self.register)
        register_button.grid(row=5, column=1, pady=20, padx=10, sticky='w')
        
        # Back to Login Button
        back_button = tk.Button(self.master, text="Back to Login", bg='grey80', fg='black', font='Helvetica 10 bold', command=self.back_to_login)
        back_button.grid(row=5, column=1, pady=20, padx=150, sticky='w')
    
    def register(self):
        fname = self.fname_box.get().strip()
        lname = self.lname_box.get().strip()
        username = self.user_box.get().strip()
        password = self.pass_box.get().strip()
        gender = self.gender_var.get()
        
        if not all([fname, lname, username, password]):
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        register_file = os.path.join("Users", "register.txt")
        credentials = {}
        if os.path.exists(register_file):
            with open(register_file, "r") as file:
                for line in file:
                    user, pwd = line.strip().split('\t')
                    credentials[user] = pwd
        
        if username in credentials:
            messagebox.showerror("Error", "Username Already Exists")
            return
        
        # Save credentials
        with open(register_file, "a") as file:
            file.write(f"{username}\t{password}\n")
        
        # Create user directory and info file
        user_dir = os.path.join("Users", username)
        os.makedirs(user_dir, exist_ok=True)
        info_file = os.path.join(user_dir, "info.txt")
        with open(info_file, "w") as file:
            file.write(f"{fname}\t{lname}\t{gender}\t{username}\t{password}\n")
        
        messagebox.showinfo("Success", "Registration Successful. Please Log In.")
        self.back_to_login()
    
    def back_to_login(self):
        self.master.destroy()
        self.login_master.deiconify()

