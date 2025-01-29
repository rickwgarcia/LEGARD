# gui/tabs/start_routine_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
from hardware.gpio_interface import GPIOInterface
from hardware.sensor_interface import SensorInterface
from utils.data_handler import DataHandler
from multiprocessing import Process, Manager, Queue
from math import acos, pi
import time
import datetime
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import numpy as np

class StartRoutineTab:
    def __init__(self, parent, gpio, sensor, username, day):
        """
        Initializes the StartRoutineTab.

        Parameters:
        - parent: The parent Tkinter widget.
        - gpio: Instance of GPIOInterface.
        - sensor: Instance of SensorInterface.
        - username: Logged-in user's username.
        - day: Current day count for the routine.
        """
        self.frame = tk.Frame(parent)
        self.gpio = gpio
        self.sensor = sensor
        self.username = username
        self.day = day
        self.setup_ui()
        self.setup_hardware()
        self.sensor_queue = Queue()
        self.process_sensor = Process(target=self.Calculations, args=(self.sensor_queue,))
        self.process_sensor.daemon = True  # Ensures the process exits when the main program does

    def setup_ui(self):
        """
        Sets up the user interface components for the Start Routine tab.
        """
        # Instruction Label
        tk.Label(
            self.frame,
            text="Stretch your leg the \nhighest you can. Then,\nclick Start.",
            font='Helvetica 20'
        ).grid(rowspan=5, column=0, padx=100)

        # Start Button
        self.start_button = tk.Button(
            self.frame,
            text="Start",
            bg='SpringGreen3',
            fg='white',
            font='Helvetica 20',
            width=10,
            height=5,
            command=self.start_routine
        )
        self.start_button.grid(rowspan=5, column=0)

        # Spacer Labels for Button States
        self.button_labels = {}
        for i in range(10):
            label = tk.Label(
                self.frame,
                text=" ",
                bg='grey40',
                fg='white',
                font='Helvetica 20',
                height=1,
                width=10
            )
            label.grid(row=i, column=1, pady=2)
            self.button_labels[i+1] = label  # Button numbers 1-10

        # Stop Button (Initially Disabled)
        self.stop_button = tk.Button(
            self.frame,
            text="Stop",
            bg='firebrick1',
            fg='white',
            font='Helvetica 20',
            height=2,
            width=10,
            state='disabled',
            command=self.stop_routine
        )
        self.stop_button.grid(row=10, column=0, columnspan=2, pady=20)

        # Matplotlib Figure for Real-Time Plotting
        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Leg Stretching Performance")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Angle (Degrees)")
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 30)

        self.line1, = self.ax.plot([], [], color='blue', label='Sensor 1 Angle')
        self.line2, = self.ax.plot([], [], color='red', label='Sensor 2 Angle')
        self.ax.legend()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=6, column=0, columnspan=2, pady=10)

        # Slider for Navigating Time
        self.ax_slider = self.fig.add_axes([0.15, 0.05, 0.7, 0.03])
        self.slider = ttk.Scale(
            self.frame,
            from_=0,
            to=1000,
            orient='horizontal',
            command=self.update_plot
        )
        self.slider.set(0)
        self.slider.grid(row=7, column=0, columnspan=2, pady=10)

        # Message Label
        self.message_var = tk.StringVar()
        self.message_var.set("")
        self.message_label = tk.Label(self.frame, textvariable=self.message_var, font='Helvetica 16', fg='green')
        self.message_label.grid(row=8, column=0, columnspan=2, pady=10)

        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            self.frame,
            orient='horizontal',
            length=400,
            mode='determinate',
            maximum=30,
            variable=self.progress_var
        )
        self.progress.grid(row=9, column=0, columnspan=2, pady=10)

    def setup_hardware(self):
        """
        Sets up GPIO event detections and initializes necessary variables.
        """
        # Define GPIO Pins
        self.ButtonPins = {
            1: 14,
            2: 15,
            3: 18,
            4: 23,
            5: 24,
            6: 25,
            7: 8,
            8: 7,
            9: 1,
            10: 12
        }

        # Initialize variables
        self.repetition_count = 0
        self.max_angle = 0
        self.avg_velocity = 0
        self.distance = 0
        self.current_angle = 0
        self.sensor1_angle = []
        self.sensor2_angle = []
        self.time_data = []
        self.start_time = None

        # Flags
        self.routine_active = False

    def start_routine(self):
        """
        Starts the stretching routine by initializing processes and enabling/disabling buttons.
        """
        if not self.routine_active:
            self.routine_active = True
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.message_var.set("Routine Started. Perform your stretches.")

            # Start the sensor data processing process
            self.process_sensor.start()

            # Start the animation
            self.ani = FuncAnimation(
                self.fig,
                self.animate,
                init_func=self.init_anim,
                interval=1000,
                blit=True
            )

    def stop_routine(self):
        """
        Stops the stretching routine, saves data, and resets the UI.
        """
        if self.routine_active:
            self.routine_active = False
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.message_var.set("Routine Stopped.")

            # Terminate the sensor processing process
            if self.process_sensor.is_alive():
                self.process_sensor.terminate()
                self.process_sensor.join()

            # Save performance data
            self.save_performance()

    def animate(self, frame):
        """
        Updates the plot with new data from the sensor process.
        """
        try:
            while not self.sensor_queue.empty():
                data = self.sensor_queue.get_nowait()
                timestamp, angle1, angle2 = data
                self.time_data.append(timestamp)
                self.sensor1_angle.append(angle1)
                self.sensor2_angle.append(angle2)

                # Update max angle
                if angle1 > self.max_angle:
                    self.max_angle = angle1

                # Update average velocity (simplified example)
                if len(self.sensor1_angle) > 1:
                    velocity = abs(self.sensor1_angle[-1] - self.sensor1_angle[-2])
                    self.avg_velocity = (self.avg_velocity * (len(self.sensor1_angle)-2) + velocity) / (len(self.sensor1_angle)-1)

                # Update distance (simplified example)
                self.distance += velocity  # Assuming distance increases with velocity

            # Update plot data
            self.line1.set_data(self.time_data, self.sensor1_angle)
            self.line2.set_data(self.time_data, self.sensor2_angle)

            # Adjust x-axis
            if self.time_data:
                self.ax.set_xlim(max(0, self.time_data[-1]-100), self.time_data[-1]+10)
                self.slider.set(float(self.time_data[-1]))

            # Update progress bar
            if self.sensor1_angle:
                self.progress_var.set(self.sensor1_angle[-1])

            return self.line1, self.line2
        except Exception as e:
            print(f"Animation Error: {e}")
            return self.line1, self.line2

    def init_anim(self):
        """
        Initializes the animation.
        """
        self.line1.set_data([], [])
        self.line2.set_data([], [])
        return self.line1, self.line2

    def update_plot(self, val):
        """
        Updates the plot based on the slider's value.
        """
        current_time = float(val)
        self.ax.set_xlim(current_time, current_time + 100)
        self.canvas.draw_idle()

    def Calculations(self, queue):
        """
        Handles sensor data processing in a separate process.

        Parameters:
        - queue: Multiprocessing Queue to send data back to the main process.
        """
        start_time = time.time()
        while True:
            if not self.routine_active:
                break
            qw = self.sensor.get_quaternion()[0]
            Rad2Deg = 180 / pi

            if qw is not None:
                try:
                    angle = round(2 * acos(qw) * Rad2Deg, 2)
                except:
                    angle = 0
            else:
                angle = 0

            # Simulate second sensor angle (for demonstration)
            angle2 = round(angle + np.random.uniform(-5, 5), 2)

            timestamp = time.time() - start_time
            queue.put((timestamp, angle, angle2))

            time.sleep(1)  # Sensor reading interval

    def save_performance(self):
        """
        Saves the performance data to the user's info file.
        """
        user, df, day = DataHandler.load_user_info(self.username)
        DataHandler.save_performance(
            self.username,
            day,
            self.info,
            self.time_data,
            self.sensor1_angle,
            self.sensor2_angle
        )
        messagebox.showinfo("Success", "Performance data saved successfully.")

    def on_close(self):
        """
        Ensures that all processes are terminated upon closing the application.
        """
        if self.routine_active:
            self.stop_routine()
        self.gpio.cleanup()
        self.frame.destroy()

