import threading
import serial
import time
import logging
import queue

class SerialThread(threading.Thread):
    """
    Continuously reads lines from the Serial Port (Wii Balance Board)
    and puts them into a shared queue.
    """
    def __init__(self, port, baudrate, data_queue):
        super().__init__(daemon=True)
        self.port = port
        self.baudrate = baudrate
        self.data_queue = data_queue
        self.serial_connection = None
        self.running = False

    def run(self):
        try:
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=1)
            self.running = True
            logging.info(f"Serial connected to {self.port}.")
        except serial.SerialException as e:
            logging.error(f"Failed to connect to {self.port}.\n{e}")
            return

        while self.running:
            try:
                # Blocking read is fine here because it's in its own thread
                line = self.serial_connection.readline().decode('utf-8').strip()
                if line:
                    self.data_queue.put(line)
            except Exception:
                break 
        
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()

    def stop(self):
        self.running = False

    def send(self, data):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(data.encode('utf-8'))
            except Exception:
                logging.error("Failed to send data; device may be disconnected.")


class SensorThread(threading.Thread):
    """
    Continuously reads the BNO055 I2C sensor in the background.
    """
    def __init__(self, sensor_object):
        super().__init__(daemon=True)
        self.sensor = sensor_object
        self.running = False
        # Default identity quaternion (w=1, x=0, y=0, z=0)
        self._latest_quaternion = (1.0, 0.0, 0.0, 0.0) 
        self._lock = threading.Lock()

    def run(self):
        self.running = True
        logging.info("Sensor thread started.")
        while self.running:
            try:
                # Hardware read
                q = self.sensor.quaternion
                if q is not None:
                    with self._lock:
                        self._latest_quaternion = q
                time.sleep(0.01) # ~100Hz refresh
            except Exception:
                time.sleep(0.1)

    def get_quaternion(self):
        """Returns the most recent valid reading instantly."""
        with self._lock:
            return self._latest_quaternion

    def stop(self):
        self.running = False