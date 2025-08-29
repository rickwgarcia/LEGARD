import serial  # For reading data from the Arduino over serial

def center_of_mass(weights):
    """Calculate X and Y values based on the weights of four sensors.

    Sensor layout (clockwise order):
        WA = front-left
        WB = front-right
        WC = back-right
        WD = back-left

         [WA] ---- [WB]
          |          |
         [WD] ---- [WC]

    Axis directions:
        x: positive if weight shifts right (WB + WC > WA + WD)
        y: positive if weight shifts forward (WA + WB > WC + WD)
    """
    WA, WB, WC, WD = weights
    W_total = WA + WB + WC + WD
    if W_total == 0:
        return 0.0, 0.0  # Avoid division by zero

    x = ((WB + WC) - (WA + WD)) / W_total
    y = ((WA + WB) - (WC + WD)) / W_total
    return x, y

def read_weight(ser):
    """Read and parse weight data from the serial connection."""
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        try:
            weights = [float(part) for part in line.split(',')]
            if len(weights) != 4:
                raise ValueError("Expected 4 values")
            return weights
        except ValueError:
            print(f"{line}")
    return None

if __name__ == '__main__':
    # Set up serial connection to Arduino
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    ser.flush()  # Clear any initial noise in the serial buffer

    while True:
        weights = read_weight(ser)
        if weights:
            x, y = center_of_mass(weights)
            print(f"{weights} -> X: {x:.3f}, Y: {y:.3f}")
