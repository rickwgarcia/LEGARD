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
velocity_data = deque(maxlen=MAX_DATA_POINTS)

# Get the start time for elapsed time calculation
start_time = time.monotonic()

# --- ADDED: Variable to store the initial angle as an offset ---
initial_angle_w = None

# --- Plot Setup ---
# Create a figure and two subplots, one above the other
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
fig.suptitle('Live BNO055 Sensor Data (Relative Angle)')

# Initialize empty line objects for our plots.
line1, = ax1.plot([], [], color='cyan', label='Angle')
line2, = ax2.plot([], [], color='lime', label='Angular Velocity')

# --- Initialization Function ---
def init():
    """Initializes the background of each plot."""
    # Setup the Angle plot (ax1)
    ax1.set_ylabel("Relative Angle (degrees)")
    ax1.set_title("Relative Angle (from Starting Position)")
    ax1.grid(True)
    ax1.set_ylim(0, 30) 

    # Setup the Velocity plot (ax2)
    # MODIFIED: Changed the label from rad/s to degrees/s
    ax2.set_ylabel("Angular Velocity (degrees/s)")
    ax2.set_title("Instantaneous Angular Velocity")
    ax2.set_xlabel("Time (s)")
    ax2.grid(True)
    # MODIFIED: Adjusted the y-axis limit to accommodate degrees
    ax2.set_ylim(0, 180)

    # Improve spacing and return the line objects
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    return line1, line2,

# --- Animation Function ---
def animate(i):
    """
    Reads sensor data, appends it, and updates the plot lines.
    """
    global initial_angle_w
    
    try:
        # --- 1. Read and Calculate New Data ---
        current_time = time.monotonic() - start_time
        angle_w = None
        velocity = None

        # Calculate angle from quaternion
        qw = sensor.quaternion[0]
        if qw is not None:
            if qw > 1.0: qw = 1.0
            if qw < -1.0: qw = -1.0
            
            current_absolute_angle = math.acos(qw) * 2 * (180 / math.pi)

            if initial_angle_w is None:
                initial_angle_w = current_absolute_angle
            
            angle_w = current_absolute_angle - initial_angle_w

        # Calculate instantaneous velocity from gyroscope
        gyro = sensor.gyro
        if gyro is not None:
            # Calculate the magnitude in rad/s
            velocity_rad = math.sqrt(gyro[0]**2 + gyro[1]**2 + gyro[2]**2)
            # MODIFIED: Convert radians/s to degrees/s
            velocity = velocity_rad * (180 / math.pi)

        # --- 2. Append Data to Lists ---
        time_data.append(current_time)
        angle_w_data.append(angle_w)
        velocity_data.append(velocity)

        # --- 3. Update Line Data ---
        line1.set_data(time_data, angle_w_data)
        line2.set_data(time_data, velocity_data)
        
        # --- 4. Rescale the Axes ---
        ax1.relim()
        ax1.autoscale_view(scalex=True, scaley=False)
        ax2.relim()
        ax2.autoscale_view(scalex=True, scaley=False)
        
        return line1, line2,

    except (OSError, RuntimeError):
        print("⚠️ Sensor read error. Skipping one reading...")
        return line1, line2,

# --- Create and run the animation ---
ani = animation.FuncAnimation(fig, animate, init_func=init, interval=20, blit=True)

# Display the plot window
plt.show()

print("Plot window closed. Program finished.")