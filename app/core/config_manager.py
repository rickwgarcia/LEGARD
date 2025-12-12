import configparser
import os

# ---------------------
# File: config_manager.py
# Author: Ricardo Garcia, ricardo.garcia@cosmiac.org
# Last Modified: 2025-12-12
# Version: 2.0.0
# ---------------------

"""
Module for loading and managing application configuration settings from
the 'config.ini' file.

The configuration file is expected to be located in the project's root 
directory, which is assumed to be one level up from the directory 
containing this configuration manager script (config_manager.py).

The path calculation ensures the configuration is always loaded correctly 
regardless of the working directory from which the application is run.
"""

config = configparser.ConfigParser()

# 1. Get the folder where THIS file (config_manager.py) lives
# Example: /home/user/LEGARD/app/core
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Go one level up to the project root
# Example: /home/user/LEGARD/app
project_root = os.path.dirname(current_dir)

# 3. Join the root path with the config filename
# Example: /home/user/LEGARD/app/config.ini
config_path = os.path.join(project_root, 'config.ini')

# 4. Read the file using the full path
# The resulting 'config' object can be accessed by other modules.
read_files = config.read(config_path)

# Debug check: provide a warning if the file could not be loaded
if not read_files:
    print(f"WARNING: Could not find config.ini at {config_path}")