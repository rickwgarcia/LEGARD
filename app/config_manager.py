import configparser
import os

# Get the absolute path of the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Create the full path to the config.ini file
CONFIG_FILE = os.path.join(script_dir, 'config.ini')

# Create a configuration parser
config = configparser.ConfigParser()



# Read the existing or newly created config file
config.read(CONFIG_FILE)