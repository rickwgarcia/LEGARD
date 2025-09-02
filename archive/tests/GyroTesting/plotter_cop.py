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
# A lock to ensure thread-safe access to the CoP data
cop_lock = threading.Lock()
# A dictionary to hold the most recent CoP data
cop_data = {"x": 0.0, "y": 0.0}

# A thread-safe queue for writing data to the CSV file
data_queue = queue.Queue()

# A flag to signal threads to stop
program_running = True

# --- CoP Reader Thread Function ---
def read_cop_thread(port, baud):
    """
    This function runs in a separate thread.
    It continuously reads from the serial port, parses the CoP data,
    and updates the shared cop_data dictionary.
    """
    global cop_data
    try:
        # Establish serial connection
        ser = serial.Serial(port, baud, timeout=1)
        print("✅ Serial port opened successfully.")
        time.sleep(2)  # Wait for Arduino to reset
        ser.write(b'c') # Send 'c' to start streaming CoP data
        print("Sent 'c' to Arduino to start CoP stream.")
    except serial.SerialException as e:
        print(f"❌ Error opening serial port {port}: {e}")
        return # Exit the thread if the port can't be opened

    while program_running:
        try:
            if ser.in_waiting > 0:
                # Read a line from Arduino, decode, and strip whitespace
                line = ser.readline().decode('utf-8').strip()
                
                # Expected format: "(x.xxx, y.yyy)"
                if line.startswith('(') and line.endswith(')'):
                    # Remove parentheses and split by comma
                    parts = line.strip('()').split(',')
                    if len(parts) == 2:
                        cop_x = float(parts[0])
                        cop_y = float(parts[1])
                        
                        # Use the lock to safely update the shared data
                        with cop_lock:
                            cop_data["x"] = cop_x
                            cop_data["y"] = cop_y
        except (ValueError, IndexError):
            # Ignore lines that can't be parsed
            pass 
        except Exception as e:
            print(f"⚠️ Error in CoP thread: {e}")
            time.sleep(1) # Avoid spamming errors
            
    ser.close()
    print("CoP thread finished and serial port closed.")

# --- CSV Writer Thread Function ---
def csv_writer_thread(filename, q):
    """
    This function runs in a separate thread.
    It waits for data to appear in the queue and writes it to a CSV file.
    """
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        # Write the header
        writer.writerow(['Time', 'Angle', 'X', 'Y'])
        print(f"✅ CSV file '{filename}' opened for writing.")
        
        while True:
            try:
                # Get data from the queue. It will block until data is available.
                data_row = q.get()
                
                # A 'None' value is our signal to stop
                if data_row is None:
                    break
                    
                writer.writerow(data_row)
                q.task_done() # Signal that the task is done
            except Exception as e:
                print(f"⚠️ Error in CSV writer thread: {e}")

    print("CSV writer thread finished.")

# --- Sensor Setup ---
# Initialize the I2C bus and BNO055 sensor
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
start_time = time.monotonic()
initial_angle_w = None

# --- Plot Setup ---
fig, ax1 = plt.subplots(1, 1)
fig.suptitle('Live Sensor Data')
line1, = ax1.plot([], [], color='cyan', label='Angle')
# Add a text object to display the live CoP coordinate
cop_text = ax1.text(0.02, 0.98, '', transform=ax1.transAxes, va='top', ha='left',
                    fontsize=12, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

def init():
    """Initializes the background of the plot."""
    ax1.set_ylabel("Relative Angle (degrees)")
    ax1.set_title("Relative Angle (from Starting Position)")
    ax1.set_xlabel("Time (s)")
    ax1.grid(True)
    ax1.set_ylim(-90, 90) # A more reasonable default Y-limit
    plt.tight_layout(rect=[0, 0.03, 1, 0.93])
    return line1, cop_text,

def animate(i):
    """
    This is the main animation loop, run by the main thread.
    """
    global initial_angle_w, cop_data
    
    current_x = None
    current_y = None
    angle_w = None
    
    # --- 1. Read BNO055 Sensor ---
    try:
        current_time = time.monotonic() - start_time
        
        # Calculate angle from quaternion
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
        # Keep old values for this frame if read fails
        angle_w = angle_w_data[-1] if angle_w_data else 0

    # --- 2. Get latest CoP data from the shared variable ---
    with cop_lock:
        current_x = cop_data["x"]
        current_y = cop_data["y"]

    # --- 3. Append data for plotting ---
    time_data.append(current_time)
    angle_w_data.append(angle_w)

    # --- 4. Queue data for CSV writing ---
    # We queue all data, even if CoP is the same as the last frame
    csv_row = [f"{current_time:.3f}", f"{angle_w:.3f}" if angle_w is not None else "", current_x, current_y]
    data_queue.put(csv_row)

    # --- 5. Update Plot ---
    line1.set_data(time_data, angle_w_data)
    cop_text.set_text(f'CoP: ({current_x:.3f}, {current_y:.3f})')
    ax1.relim()
    ax1.autoscale_view(scalex=True, scaley=True) # Autoscale Y for better viewing
    
    return line1, cop_text,

# --- Main Program Execution ---
if __name__ == "__main__":
    # 1. Create and start the background threads
    cop_reader = threading.Thread(target=read_cop_thread, args=(SERIAL_PORT, BAUD_RATE))
    csv_writer = threading.Thread(target=csv_writer_thread, args=(CSV_FILENAME, data_queue))

    cop_reader.start()
    csv_writer.start()

    # 2. Create and run the matplotlib animation in the main thread
    ani = animation.FuncAnimation(fig, animate, init_func=init, interval=20, blit=True)
    plt.show()

    # 3. After the plot window is closed, signal threads to stop
    print("Plot window closed. Shutting down...")
    program_running = False
    data_queue.put(None) # Signal for the CSV writer to finish

    # 4. Wait for threads to complete their cleanup
    cop_reader.join()
    csv_writer.join()

    print("Program finished gracefully.")
