import configparser
import os

config = configparser.ConfigParser()

# 1. Get the folder where THIS file (config_manager.py) lives
# Result: .../LEGARD/app/core
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Go one level up to the project root
# Result: .../LEGARD/app
project_root = os.path.dirname(current_dir)

# 3. Join the root path with the config filename
config_path = os.path.join(project_root, 'config.ini')

# 4. Read the file using the full path
read_files = config.read(config_path)

# Debug check (Optional: prints if it found the file)
if not read_files:
    print(f"WARNING: Could not find config.ini at {config_path}")