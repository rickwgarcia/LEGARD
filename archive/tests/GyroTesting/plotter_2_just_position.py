import time
import board
import adafruit_bno055
import math
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- Sensor Setup ---
# Initialize the I2C bus and BNO055 sensor
i2c = board.I2C()
try:
    sensor = adafruit_bno055.BNO055_I2C(i2c)
    print("✅ BNO055 sensor found!")
except (ValueError, OSError):
    print("❌ BNO055 sensor not found. Please check your wiring.")
    exit()

# --- Data Storage Setup ---
# Use deque for efficient adding and removing of old data
MAX_DATA_POINTS = 100  # How many points to display on the graph
time_data = deque(maxlen=MAX_DATA_POINTS)
angle_w_data = deque(maxlen=MAX_DATA_POINTS)

# Get the start time for elapsed time calculation
start_time = time.monotonic()

# --- ADDED: Variable to store the initial angle as an offset ---
initial_angle_w = None

# --- Plot Setup ---
# Create a figure and a single subplot
fig, ax1 = plt.subplots(1, 1)
fig.suptitle('Live BNO055 Sensor Data (Relative Angle)')

# Initialize an empty line object for our plot.
line1, = ax1.plot([], [], color='cyan', label='Angle')

# --- Initialization Function ---
def init():
    """Initializes the background of the plot."""
    # Setup the Angle plot (ax1)
    ax1.set_ylabel("Relative Angle (degrees)")
    ax1.set_title("Relative Angle (from Starting Position)")
    ax1.set_xlabel("Time (s)")
    ax1.grid(True)
    ax1.set_ylim(0, 30)

    # Improve spacing and return the line object
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    return line1,

# --- Animation Function ---
def animate(i):
    """
    Reads sensor data, appends it, and updates the plot line.
    """
    global initial_angle_w
    
    try:
        # --- 1. Read and Calculate New Data ---
        current_time = time.monotonic() - start_time
        angle_w = None

        # Calculate angle from quaternion
        qw = sensor.quaternion[0]
        if qw is not None:
            if qw > 1.0: qw = 1.0
            if qw < -1.0: qw = -1.0
            
            current_absolute_angle = math.acos(qw) * 2 * (180 / math.pi)

            if initial_angle_w is None:
                initial_angle_w = current_absolute_angle
            
            angle_w = current_absolute_angle - initial_angle_w

        # --- 2. Append Data to Lists ---
        time_data.append(current_time)
        angle_w_data.append(angle_w)

        # --- 3. Update Line Data ---
        line1.set_data(time_data, angle_w_data)
        
        # --- 4. Rescale the Axes ---
        ax1.relim()
        ax1.autoscale_view(scalex=True, scaley=False)
        
        return line1,

    except (OSError, RuntimeError):
        print("⚠️ Sensor read error. Skipping one reading...")
        return line1,

# --- Create and run the animation ---
ani = animation.FuncAnimation(fig, animate, init_func=init, interval=20, blit=True)

# Display the plot window
plt.show()

print("Plot window closed. Program finished.")