# legard_app/data/user_manager.py

import os
import pandas as pd
import datetime
from config import USERS_DIR, REGISTER_FILE

class UserManager:
    """Handles all user-related data operations."""

    def __init__(self, username=None):
        self.username = username
        self.user_info = None
        self.history_df = None
        if username:
            self.load_user_data()

    def login(self, username, password):
        """Validates user credentials."""
        if not os.path.exists(REGISTER_FILE):
            return False
        with open(REGISTER_FILE, "r") as file:
            for line in file:
                creds = line.split()
                if len(creds) == 2 and username == creds[0] and password == creds[1]:
                    self.username = username
                    self.load_user_data()
                    return True
        return False

    def register(self, first, last, gender, username, password):
        """Registers a new user."""
        if not username or not password:
            return "empty_credentials"

        os.makedirs(USERS_DIR, exist_ok=True)
        if not os.path.exists(REGISTER_FILE):
            with open(REGISTER_FILE, "w"): pass # create empty file

        with open(REGISTER_FILE, "r+") as file:
            for line in file:
                if username == line.split()[0]:
                    return "user_exists"
            # If loop finishes, user doesn't exist, so add them
            file.write(f"{username}\t{password}\n")

        # Create user-specific directory and info file
        user_dir = os.path.join(USERS_DIR, username)
        os.makedirs(user_dir, exist_ok=True)
        with open(os.path.join(user_dir, "info.txt"), "w") as file:
            file.write(f"{first}\t{last}\t{gender}\t{username}\t{password}\n")
        
        return "success"

    def load_user_data(self):
        """Loads user info and history into memory."""
        if not self.username:
            return
        
        info_file_path = os.path.join(USERS_DIR, self.username, "info.txt")
        user = []
        df = pd.DataFrame(columns=['Day', 'Value'])

        with open(info_file_path, "r") as file:
            for i, f in enumerate(file):
                if i == 0:
                    user.append(f.split())
                else:
                    line = f.split()
                    df = df.append({'Day': line[0], 'Value': [int(line[1]), int(line[2]), int(line[3])]}, ignore_index=True)
        
        self.user_info = user[0] if user else None
        self.history_df = df

    def get_day_number(self):
        """Returns the number for the next session day."""
        if self.history_df is not None:
            return len(self.history_df) + 1
        return 1
        
    def get_session_files(self):
        """Returns a list of saved session files for the user."""
        if not self.username:
            return []
        path = os.path.join(USERS_DIR, self.username)
        # Filter out info.txt to only get session data files
        return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f != 'info.txt']

    def save_session(self, day_num, reps, session_time, rest_time, full_log, cartesian_log):
        """Saves the completed session data to files."""
        # 1. Save the detailed log for the day
        current_time = datetime.datetime.now()
        filename = f"{datetime.date.today()}_{current_time.hour}_{current_time.minute}.txt"
        filepath = os.path.join(USERS_DIR, self.username, filename)

        with open(filepath, "w") as f:
            f.write(full_log)
            # Add cartesian data if available
            if cartesian_log:
                f.write("\nX Cord\tY Cord\n")
                f.write(cartesian_log)

        # 2. Append the summary to info.txt
        info_file_path = os.path.join(USERS_DIR, self.username, "info.txt")
        with open(info_file_path, "a") as file:
            file.write(f"Day{day_num}\t{reps}\t{session_time}\t{rest_time}\n")
