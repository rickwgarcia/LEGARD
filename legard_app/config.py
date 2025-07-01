# legard_app/config.py

import RPi.GPIO as GPIO

# GPIO Pin Configuration
# Using Board pin numbering can be less confusing than BCM on different Pi models.
# Let's stick with BCM as in the original code.
GPIO_MODE = GPIO.BCM

# Mapping pins to their function for clarity
PINS = {
    'stretch_1': 14,
    'stretch_2': 15,
    'stretch_3': 18,
    'stretch_4': 23,
    'stretch_5': 24,
    'stretch_6': 25,
    'stretch_7': 8,
    'stretch_8': 7,
    'stretch_9': 1,
    'stretch_10': 12,
}

# The pins used during the main routine after setting the max stretch
# These correspond to the original ButtonPin, ButtonPin2, ButtonPin3
ROUTINE_PINS = {
    'start_repetition': 'stretch_1', # This will be re-mapped based on max stretch
    'target_reached': 'stretch_2',   # This will be re-mapped
    'target_ surpassed': 'stretch_3' # This will be re-mapped
}


# I2C Configuration
I2C_BUS = 1
SENSOR_1_ADDRESS = 0x28
SENSOR_2_ADDRESS = 0x29

# File Paths
USERS_DIR = "Users"
REGISTER_FILE = f"{USERS_DIR}/register.txt"
DEFAULT_PROFILE_PIC = "/home/si/Desktop/LEGARD/app/prof_pic.png"

# Plotting & UI
PLOT_BG_COLOR = '#E0E0E0'

# Routine Logic
MAX_SETS = 3
REST_TIME_PER_REP_SECONDS = 20 # Original code: btn2[9]*20
