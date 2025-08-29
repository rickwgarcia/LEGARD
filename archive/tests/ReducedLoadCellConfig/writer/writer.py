import serial  # For reading data from the Arduino over serial
import datetime # For generating timestamps and filenames
import os      # For path manipulation

def center_of_mass(weights):
    """Calculate X and Y values based on the weights of four sensors.
    (Your existing function - no changes here)
    """
    WA, WB, WC, WD = weights
    W_total = WA + WB + WC + WD
    if W_total == 0:
        return 0.0, 0.0

    x = ((WB + WC) - (WA + WD)) / W_total
    y = ((WA + WB) - (WC + WD)) / W_total
    return x, y

def read_weight(ser):
    """Read and parse weight data from the serial connection.
    Ensures that individual raw weights are not negative (clamped at 0.0).
    (Your existing function - no changes here)
    """
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        try:
            parsed_weights = [float(part) for part in line.split(',')]
            if len(parsed_weights) != 4:
                raise ValueError(f"Expected 4 values, got {len(parsed_weights)}")
            processed_weights = [max(0.0, w) for w in parsed_weights]
            return processed_weights
        except ValueError as e:
            print(f"Error parsing line '{line}': {e}")
    return None

if __name__ == '__main__':
    # --- Configuration ---
    serial_port = '/dev/ttyACM0'
    baud_rate = 9600

    # --- Get the directory where the script is located ---
    # __file__ is a special variable that holds the path of the current script
    # os.path.abspath(__file__) gets the absolute path to the script
    # os.path.dirname(...) gets the directory part of that path
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # --- Generate dynamic filename based on current time script starts ---
    script_start_time = datetime.datetime.now()
    base_filename = script_start_time.strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
    
    # --- Join the script's directory path and the base filename ---
    # This ensures the log file is saved in the same folder as the script.
    output_filename = os.path.join(script_directory, base_filename)

    ser = None
    try:
        ser = serial.Serial(serial_port, baud_rate, timeout=1)
        ser.flush()
        print(f"Serial connection established on {serial_port} at {baud_rate} baud.")
        print(f"Logging data to a new file: {output_filename}. Press Ctrl+C to stop.")

        with open(output_filename, 'w') as data_file:
            data_file.write(f"# Data log started at: {script_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            data_file.write(f"# Serial Port: {serial_port}, Baud Rate: {baud_rate}\n")
            data_file.write("# Format: Timestamp | [WA, WB, WC, WD] -> X: CoM_X, Y: CoM_Y\n")
            data_file.write("# -----\n")
            data_file.flush()

            while True:
                weights = read_weight(ser)
                if weights:
                    x, y = center_of_mass(weights)
                    entry_timestamp_obj = datetime.datetime.now()
                    entry_timestamp_str = entry_timestamp_obj.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    output_string = f"{entry_timestamp_str} | {weights} -> X: {x:.3f}, Y: {y:.3f}"
                    print(output_string)
                    data_file.write(output_string + "\n")
                    data_file.flush()

    except serial.SerialException as e:
        print(f"Serial communication error: {e}")
        print("Please check the port and ensure the Arduino is connected.")
    except KeyboardInterrupt:
        print("\nLogging stopped by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("Serial connection closed.")
        if 'output_filename' in locals():
            print(f"Data logging session finished. Data saved to {output_filename}")
        else:
            print("Script terminated before logging could start or filename was generated.")