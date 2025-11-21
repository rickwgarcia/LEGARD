import csv
import hashlib
import os
from config_manager import config

# Get path from config
USER_DATA_FILE = config.get('Paths', 'user_data_file')

def setup_files():
    """Ensures the user data directory and CSV exist."""
    user_dir = os.path.dirname(USER_DATA_FILE)
    if user_dir and not os.path.exists(user_dir):
        os.makedirs(user_dir)
    if not os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['username', 'hashed_pin', 'first_name', 'last_name', 'gender'])

def hash_pin(pin):
    salt = "your_secret_salt" 
    salted_pin = pin + salt
    return hashlib.sha256(salted_pin.encode()).hexdigest()

def register_user(username, pin, first_name, last_name, gender):
    if not all([username, pin, first_name, last_name, gender]):
        return (False, "All fields are required.")
    
    # Ensure file exists
    setup_files() 
    
    # Check for duplicate username
    with open(USER_DATA_FILE, 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader, None) # Skip header
        for row in reader:
            if row and row[0] == username:
                return (False, "Username already exists.")
    
    hashed_pin = hash_pin(pin)
    with open(USER_DATA_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, hashed_pin, first_name, last_name, gender])
        
    return (True, f"Account for '{username}' created successfully!")

def login_user(username, pin):
    if not username or not pin:
        return (False, "Username and PIN cannot be empty.", None, None)
    
    if not os.path.exists(USER_DATA_FILE):
        setup_files()
        return (False, "No user accounts found. Please register an account.", None, None)
        
    hashed_pin = hash_pin(pin)
    with open(USER_DATA_FILE, 'r', newline='') as file:
        reader = csv.reader(file)
        try: 
            next(reader) # Skip header
        except StopIteration: 
            return (False, "No user accounts found.", None, None)
        
        for row in reader:
            # Ensure row has enough columns to avoid index errors
            if len(row) >= 5 and row[0] == username and row[1] == hashed_pin:
                full_name = f"{row[2]} {row[3]}"
                gender = row[4]
                return (True, f"Welcome back, {full_name}!", full_name, gender)
                
    return (False, "Invalid username or PIN.", None, None)