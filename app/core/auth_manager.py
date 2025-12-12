import csv
import hashlib
import os
from core.config_manager import config

# ---------------------
# File: auth_manager.py
# Author: Ricardo Garcia, ricardo.garcia@cosmiac.org
# Last Modified: 2025-12-12
# Version: 2.0.0
# ---------------------

"""
Module for handling user authentication, including registration and login,
by storing user data in a local CSV file.
"""

# Get path from config
USER_DATA_FILE = config.get('Paths', 'user_data_file')

def setup_files():
    """
    Ensures the user data directory and the user data CSV file exist.

    If the directory does not exist, it is created. If the CSV file does not 
    exist, it is created with the necessary header row:
    ['username', 'hashed_pin', 'first_name', 'last_name', 'gender'].
    """
    user_dir = os.path.dirname(USER_DATA_FILE)
    if user_dir and not os.path.exists(user_dir):
        os.makedirs(user_dir)
    if not os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['username', 'hashed_pin', 'first_name', 'last_name', 'gender'])

def hash_pin(pin):
    """
    Generates a secure SHA256 hash of a user's PIN using a secret salt.

    This function should be used for both registration and login attempts 
    to ensure consistent hashing.

    Args:
        pin (str): The plain-text PIN provided by the user.

    Returns:
        str: The hexadecimal SHA256 hash of the salted PIN.
    """
    salt = "your_secret_salt" 
    salted_pin = pin + salt
    return hashlib.sha256(salted_pin.encode()).hexdigest()

def register_user(username, pin, first_name, last_name, gender):
    """
    Registers a new user account by writing their data to the CSV file.

    It first checks for completeness of fields and then verifies if the 
    username already exists before hashing the PIN and appending the 
    new record.

    Args:
        username (str): The unique username for the account.
        pin (str): The plain-text PIN to be hashed.
        first_name (str): The user's first name.
        last_name (str): The user's last name.
        gender (str): The user's gender.

    Returns:
        tuple: A tuple containing:
               - bool: Success status (True/False).
               - str: A descriptive message.
    """
    if not all([username, pin, first_name, last_name, gender]):
        return (False, "All fields are required.")
    
    setup_files() 
    
    with open(USER_DATA_FILE, 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            if row and row[0] == username:
                return (False, "Username already exists.")
    
    hashed_pin = hash_pin(pin)
    with open(USER_DATA_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, hashed_pin, first_name, last_name, gender])
        
    return (True, f"Account for '{username}' created successfully!")

def login_user(username, pin):
    """
    Authenticates a user by checking their credentials against the stored data.

    The provided PIN is hashed and compared to the stored hash in the CSV file.

    Args:
        username (str): The username provided by the user.
        pin (str): The plain-text PIN provided by the user.

    Returns:
        tuple: A tuple containing:
               - bool: Success status (True/False).
               - str: A descriptive message (e.g., welcome or error).
               - str or None: The user's full name if successful, otherwise None.
               - str or None: The user's gender if successful, otherwise None.
    """
    if not username or not pin:
        return (False, "Username and PIN cannot be empty.", None, None)
    
    if not os.path.exists(USER_DATA_FILE):
        setup_files()
        return (False, "No user accounts found. Please register an account.", None, None)
        
    hashed_pin = hash_pin(pin)
    with open(USER_DATA_FILE, 'r', newline='') as file:
        reader = csv.reader(file)
        try: 
            next(reader)
        except StopIteration: 
            return (False, "No user accounts found.", None, None)
        
        for row in reader:
            if len(row) >= 5 and row[0] == username and row[1] == hashed_pin:
                full_name = f"{row[2]} {row[3]}"
                gender = row[4]
                return (True, f"Welcome back, {full_name}!", full_name, gender)
                
    return (False, "Invalid username or PIN.", None, None)