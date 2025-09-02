import time
import board
import adafruit_bno055
import math
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import serial
import queue
import csv

# --- User Configuration ---
SERIAL_PORT = '/dev/ttyUSB0'  #<-- IMPORTANT: Change this to your Arduino's port!
BAUD_RATE = 9600
CSV_FILENAME = 'sensor_data.csv'

# --- Global Shared Data & Thread Control ---
cop_lock = threading.Lock()
cop_data = {"x": 0.0, "y": 0.0}
data_queue = queue.Queue()
program_running = True

# --- CoP Reader Thread Function (No changes needed) ---
def read_cop_thread(port, baud):
    """
    This function runs in a separate thread.
    It continuously reads from the serial port, parses the CoP data,
    and updates the shared cop_data dictionary.
    """
    global cop_data
    try:
        ser = serial.Serial(port, baud, timeout=1)
        print("✅ Serial port opened successfully.")
        time.sleep(2)
        ser.write(b'c')
        print("Sent 'c' to Arduino to start CoP stream.")
    except serial.SerialException as e:
        print(f"❌ Error opening serial port {port}: {e}")
        return

    while program_running:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if line.startswith('(') and line.endswith(')'):
                    parts = line.strip('()').split(',')
                    if len(parts) == 2:
                        cop_x = float(parts[0])
                        cop_y = float(parts[1])
                        with cop_lock:
                            cop_data["x"] = cop_x
                            cop_data["y"] = cop_y
        except (ValueError, IndexError):
            pass
        except Exception as e:
            print(f"⚠️ Error in CoP thread: {e}")
            time.sleep(1)
            
    ser.close()
    print("CoP thread finished and serial port closed.")

# --- CSV Writer Thread Function (No changes needed) ---
def csv_writer_thread(filename, q):
    """
    This function runs in a separate thread.
    It waits for data to appear in the queue and writes it to a CSV file.
    """
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Time', 'Angle', 'X', 'Y'])
        print(f"✅ CSV file '{filename}' opened for writing.")
        while True:
            try:
                data_row = q.get()
                if data_row is None:
                    break
                writer.writerow(data_row)
                q.task_done()
            except Exception as e:
                print(f"⚠️ Error in CSV writer thread: {e}")
    print("CSV writer thread finished.")

# --- Sensor Setup ---
i2c = board.I2C()
try:
    sensor = adafruit_bno055.BNO055_I2C(i2c)
    print("✅ BNO055 sensor found!")
except (ValueError, OSError):
    print("❌ BNO055 sensor not found. Please check your wiring.")
    exit()

# --- Data Storage for Plotting ---
MAX_DATA_POINTS = 100
time_data = deque(maxlen=MAX_DATA_POINTS)
angle_w_data = deque(maxlen=MAX_DATA_POINTS)
cop_x_data = deque(maxlen=MAX_DATA_POINTS) # <-- NEW: Deque for CoP X-coordinates
cop_y_data = deque(maxlen=MAX_DATA_POINTS) # <-- NEW: Deque for CoP Y-coordinates
start_time = time.monotonic()
initial_angle_w = None

# --- Plot Setup ---
# Create a figure with two subplots side-by-side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6)) # <-- MODIFIED
fig.suptitle('Live Sensor Data')

# Setup for the first plot (Angle)
line1, = ax1.plot([], [], color='cyan', label='Angle')
cop_text = ax1.text(0.02, 0.98, '', transform=ax1.transAxes, va='top', ha='left',
                    fontsize=12, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Setup for the second plot (CoP Trajectory)
line2, = ax2.plot([], [], color='magenta', marker='.', linestyle='-', label='CoP Path') # <-- NEW

def init():
    """Initializes the background of both plots."""
    # Setup the Angle plot (ax1)
    ax1.set_ylabel("Relative Angle (degrees)")
    ax1.set_title("Angle vs. Time")
    ax1.set_xlabel("Time (s)")
    ax1.grid(True)
    
    # Setup the CoP Trajectory plot (ax2)
    ax2.set_title("CoP Trajectory") # <-- NEW
    ax2.set_xlabel("X Coordinate") # <-- NEW
    ax2.set_ylabel("Y Coordinate") # <-- NEW
    ax2.set_xlim(-1.1, 1.1)        # <-- NEW: Set fixed limits for a stable view
    ax2.set_ylim(-1.1, 1.1)        # <-- NEW
    ax2.grid(True)                 # <-- NEW
    ax2.set_aspect('equal', adjustable='box') # <-- NEW: Ensures X and Y axes have the same scale

    plt.tight_layout(rect=[0, 0.03, 1, 0.93])
    return line1, line2, cop_text, # <-- MODIFIED

def animate(i):
    """The main animation loop, which updates both plots."""
    global initial_angle_w, cop_data
    
    current_x = None
    current_y = None
    angle_w = None
    
    # --- 1. Read BNO055 Sensor ---
    try:
        current_time = time.monotonic() - start_time
        qw = sensor.quaternion[0]
        if qw is not None:
            if qw > 1.0: qw = 1.0
            if qw < -1.0: qw = -1.0
            current_absolute_angle = math.acos(qw) * 2 * (180 / math.pi)
            if initial_angle_w is None:
                initial_angle_w = current_absolute_angle
            angle_w = current_absolute_angle - initial_angle_w
    except (OSError, RuntimeError):
        print("⚠️ BNO055 read error. Skipping one reading...")
        angle_w = angle_w_data[-1] if angle_w_data else 0

    # --- 2. Get latest CoP data ---
    with cop_lock:
        current_x = cop_data["x"]
        current_y = cop_data["y"]

    # --- 3. Append data for plotting ---
    time_data.append(current_time)
    angle_w_data.append(angle_w)
    cop_x_data.append(current_x) # <-- NEW
    cop_y_data.append(current_y) # <-- NEW

    # --- 4. Queue data for CSV writing ---
    csv_row = [f"{current_time:.3f}", f"{angle_w:.3f}" if angle_w is not None else "", current_x, current_y]
    data_queue.put(csv_row)

    # --- 5. Update Plots ---
    # Update Angle plot
    line1.set_data(time_data, angle_w_data)
    cop_text.set_text(f'CoP: ({current_x:.3f}, {current_y:.3f})')
    ax1.relim()
    ax1.autoscale_view(scalex=True, scaley=True)

    # Update CoP plot
    line2.set_data(cop_x_data, cop_y_data) # <-- NEW
    
    return line1, line2, cop_text, # <-- MODIFIED

# --- Main Program Execution ---
if __name__ == "__main__":
    cop_reader = threading.Thread(target=read_cop_thread, args=(SERIAL_PORT, BAUD_RATE))
    csv_writer = threading.Thread(target=csv_writer_thread, args=(CSV_FILENAME, data_queue))
    cop_reader.start()
    csv_writer.start()

    ani = animation.FuncAnimation(fig, animate, init_func=init, interval=20, blit=True)
    plt.show()

    print("Plot window closed. Shutting down...")
    program_running = False
    data_queue.put(None)
    cop_reader.join()
    csv_writer.join()
    print("Program finished gracefully.")
