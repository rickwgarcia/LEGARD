import threading
import serial
import time
import logging
import queue


# ---------------------
# File: data_inputs.py
# Author: Ricardo Garcia, ricardo.garcia@cosmiac.org
# Last Modified: 2025-12-12
# Version: 2.0.0
# ---------------------

"""
Module providing threaded classes for concurrent hardware interaction.

It contains SerialThread for reading line-based data from a serial device 
and SensorThread for continuously polling a hardware sensor object.
Both threads run in the background as daemon threads.
"""

class SerialThread(threading.Thread):
    """
    A separate thread for continuously reading lines from a Serial Port 
    and placing them into a shared queue for processing by the main application.

    This ensures that the main thread is not blocked waiting for serial data.
    """
    def __init__(self, port, baudrate, data_queue):
        """
        Initializes the serial communication thread.

        Args:
            port (str): The serial port path (e.g., 'COM3' or '/dev/ttyACM0').
            baudrate (int): The baud rate for the serial connection.
            data_queue (queue.Queue): A thread-safe queue to deposit read lines.
        """
        super().__init__(daemon=True)
        self.port = port
        self.baudrate = baudrate
        self.data_queue = data_queue
        self.serial_connection = None
        self.running = False

    def run(self):
        """
        The main thread execution loop.

        Attempts to establish a serial connection and, if successful, 
        continuously reads line-delimited data and puts it into the queue. 
        Closes the connection upon exiting the loop.
        """
        try:
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=1)
            self.running = True
            logging.info(f"Serial connected to {self.port}.")
        except serial.SerialException as e:
            logging.error(f"Failed to connect to {self.port}.\n{e}")
            return

        while self.running:
            try:
                # The blocking nature of readline() is intentional here
                line = self.serial_connection.readline().decode('utf-8').strip()
                if line:
                    self.data_queue.put(line)
            except Exception:
                break 
        
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()

    def stop(self):
        """Signals the thread to stop execution and close the connection."""
        self.running = False

    def send(self, data):
        """
        Sends data (string) to the connected serial device.

        Args:
            data (str): The string data to encode and send over the serial port.
        """
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(data.encode('utf-8'))
            except Exception:
                logging.error("Failed to send data; device may be disconnected.")


class SensorThread(threading.Thread):
    """
    A dedicated thread for continuously polling an I2C sensor object (e.g., BNO055) 
    and safely storing the latest reading.

    This prevents slow hardware reads from blocking the main application loop.
    """
    def __init__(self, sensor_object):
        """
        Initializes the sensor polling thread.

        Args:
            sensor_object (Adafruit_BNO055 or similar): An object with a 
                                                        '.quaternion' property 
                                                        for reading sensor data.
        """
        super().__init__(daemon=True)
        self.sensor = sensor_object
        self.running = False
        self._latest_quaternion = (1.0, 0.0, 0.0, 0.0) 
        self._lock = threading.Lock()

    def run(self):
        """
        The main thread execution loop.

        Continuously reads the sensor's quaternion property, updates the 
        internal state using a lock to ensure thread safety, and sleeps briefly 
        to control the polling rate (~100Hz).
        """
        self.running = True
        logging.info("Sensor thread started.")
        while self.running:
            try:
                q = self.sensor.quaternion
                if q is not None:
                    with self._lock:
                        self._latest_quaternion = q
                time.sleep(0.01)
            except Exception:
                # Sleep longer on error to prevent CPU hogging
                time.sleep(0.1)

    def get_quaternion(self):
        """
        Retrieves the most recent quaternion reading in a thread-safe manner.

        Returns:
            tuple: The latest quaternion reading (w, x, y, z).
        """
        with self._lock:
            return self._latest_quaternion

    def stop(self):
        """Signals the thread to stop execution."""
        self.running = False