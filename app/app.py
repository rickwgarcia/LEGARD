#!/usr/bin/env python3
"""
LEGARD Application – Reorganized Structure

This version reorganizes the code into clearly defined sections:
1. Imports (grouped by standard libraries, third-party libraries, etc.)
2. The Frames class:
   • popup()         – Displays the login/registration popup.
   • MainScreen()    – Sets up the main application window with tabs.
   • Start2()        – Handles the sensor routine and graphical display.
3. Main entry point – Creates the initial Tk window and starts the popup.
All functionality remains identical.
"""

###############################
#        IMPORTS              #
###############################

# Standard libraries
import os
import time
import datetime
from math import acos, pi
from itertools import count
from sys import argv

# Multiprocessing
from multiprocessing import Process, Manager

# Tkinter and related modules
from tkinter import *
import tkinter.font as font
from tkinter import ttk, messagebox

# PIL for image handling
from PIL import ImageTk, Image

# Data handling libraries
import pandas as pd
import numpy as np

# Matplotlib for plotting
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import Slider
from matplotlib.animation import FuncAnimation

# GPIO and Sensor Libraries
import RPi.GPIO as GPIO
import smbus
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055

###############################
#        MAIN CLASS           #
###############################

class Frames:
    def popup(self, pop):
        """
        Display the login/registration popup.
        """
        # Set up the popup window
        width = pop.winfo_screenwidth()
        height = pop.winfo_screenheight()
        pop.geometry("%dx%d" % (width, height))
        pop['bg'] = 'white'
        pop.title('Log In')
        self.query = StringVar()  # For passing user info

        #################################
        # Login Functionality           #
        #################################
        def login(username, password):
            credentials_list = []
            no_user = Label(pop, text="Credentials Not Found", font='Helvetica 10 bold', bg='white')
            user_found = Label(pop, text="Welcome " + str(username), font='Helvetica 10 bold', bg='white')
            with open("Users/register.txt", "r") as file:
                for line in file:
                    credentials_list.append(line.split())
                for i, credentials in enumerate(credentials_list):
                    if username == credentials[0] and password == credentials[1]:
                        no_user.grid_forget()
                        user_found.grid(row=10, columnspan=4, sticky='ew', ipady=20)
                        self.MainScreen()
                        break
                    elif i == len(credentials_list) - 1:
                        user_found.grid_forget()
                        no_user.grid(row=10, columnspan=4, sticky='ew', ipady=20)

        #################################
        # Registration Functionality    #
        #################################
        def register(first, last, gender, username, password):
            credentials_list = []
            add_credentials = 0
            user_exists = Label(pop, text="Username Already Exists", font='Helvetica 10 bold', bg='white')
            reg_success = Label(pop, text="Username Registered Succesfully. Proceed to Login", font='Helvetica 10 bold', bg='white')
            reg_not_success = Label(pop, text="Please Enter Username and Password", font='Helvetica 10 bold', bg='white')
            with open("Users/register.txt", "r") as file:
                for line in file:
                    credentials_list.append(line.split())
                for i, credentials in enumerate(credentials_list):
                    if username == "":
                        reg_not_success.grid(row=10, columnspan=4, sticky='ew', ipady=20)
                        add_credentials = 0
                        break
                    elif username == credentials[0]:
                        user_exists.grid(row=10, columnspan=4, sticky='ew', ipady=20)
                        add_credentials = 0
                        break
                    elif i == len(credentials_list) - 1 and username != credentials[0]:
                        add_credentials = 1
                        break
            if add_credentials == 1:
                with open("Users/register.txt", "a") as file:
                    file.write(username + '\t' + password + '\n')
                os.mkdir("Users/" + username)
                with open("Users/" + username + "/info.txt", "a") as file:
                    file.write(first + '\t' + last + '\t' + gender + '\t' + username + '\t' + password + '\n')
                user_exists.grid_forget()
                reg_not_success.grid_forget()
                reg_success.grid(row=10, columnspan=4, sticky='ew', ipady=20)

        #################################
        # GUI Layout for Login/Register #
        #################################
        User = Label(pop, text="User: ", font='Helvetica 15 bold', bg='white')
        User.grid(row=2, column=0, pady=30)
        UserBox = Entry(pop, font='Helvetica 15', textvariable=self.query)
        UserBox.grid(row=2, column=1)

        Password = Label(pop, text="Password: ", font='Helvetica 15 bold', bg='white')
        Password.grid(row=3, column=0)
        PassBox = Entry(pop, font='Helvetica 15', show="*")
        PassBox.grid(row=3, column=1)

        def Lbutton():
            u = UserBox.get()
            p = PassBox.get()
            login(u, p)
            UserBox.delete(0, END)
            PassBox.delete(0, END)

        OkButton = Button(pop, text="Log In", bg='SpringGreen3', fg='black', font='Helvetica 10 bold', command=Lbutton)
        OkButton.grid(row=4, column=1, ipadx=10, ipady=6, padx=30)

        # Registration Entries (initially hidden)
        FName = Label(pop, text="First Name: ", font='Helvetica 12 bold', bg='white')
        FNameBox = Entry(pop, width=10, font='Helvetica 12')
        LName = Label(pop, text="Last Name: ", font='Helvetica 12 bold', bg='white')
        LNameBox = Entry(pop, width=10, font='Helvetica 12')
        UserReg = Label(pop, text="User: ", font='Helvetica 12 bold', bg='white')
        UserBoxReg = Entry(pop, width=10, font='Helvetica 12')
        Gender = Label(pop, text="Gender: ", font='Helvetica 12 bold', bg='white')
        ma = IntVar()
        fe = IntVar()
        Mcb = Checkbutton(pop, text="Male", bg='white', variable=ma)
        Fcb = Checkbutton(pop, text="Female", bg='white', variable=fe)
        PasswordReg = Label(pop, text="Password: ", font='Helvetica 12 bold', bg='white')
        PassBoxReg = Entry(pop, width=10, font='Helvetica 12', show="*")

        def Rbutton():
            no_entry = Label(pop, text="Fill All Boxes", font='Helvetica 12 bold', bg='white')
            f = FNameBox.get()
            l = LNameBox.get()
            u = UserBoxReg.get()
            p = PassBoxReg.get()
            if f == '' or l == '' or u == '' or p == '':
                no_entry.grid(row=10, columnspan=4, sticky='ew', ipady=20)
                return
            if fe.get() == 1:
                g = "Female"
            elif ma.get() == 1:
                g = "Male"
            else:
                g = "NotSelected"
            register(f, l, g, u, p)
            ma.set(0)
            fe.set(0)
            FNameBox.delete(0, END)
            LNameBox.delete(0, END)
            UserBoxReg.delete(0, END)
            PassBoxReg.delete(0, END)
            return

        OkButtonReg = Button(pop, text="Register", bg='SpringGreen3', fg='black', font='Helvetica 10 bold', command=Rbutton)

        def ShowLogInEntries():
            FName.grid_forget()
            FNameBox.grid_forget()
            LName.grid_forget()
            LNameBox.grid_forget()
            Gender.grid_forget()
            Mcb.grid_forget()
            Fcb.grid_forget()
            UserReg.grid_forget()
            UserBoxReg.grid_forget()
            PasswordReg.grid_forget()
            PassBoxReg.grid_forget()
            OkButtonReg.grid_forget()
            User.grid(row=2, column=0, pady=20)
            UserBox.grid(row=2, column=1)
            Password.grid(row=3, column=0, pady=20)
            PassBox.grid(row=3, column=1)
            OkButton.grid(row=4, column=1, ipadx=10, ipady=6, padx=30)

        def ShowRegEntries():
            User.grid_forget()
            UserBox.grid_forget()
            Password.grid_forget()
            PassBox.grid_forget()
            OkButton.grid_forget()
            FName.grid(row=6, column=0, sticky='e', pady=20)
            FNameBox.grid(row=6, column=1, sticky='w', pady=20)
            LName.grid(row=6, column=2, sticky='w', pady=20)
            LNameBox.grid(row=6, column=3, sticky='w', pady=20)
            Gender.grid(row=7, column=0, sticky='e', pady=20)
            Mcb.grid(row=7, column=1, sticky='w', pady=20)
            Fcb.grid(row=7, column=2, sticky='w', pady=20)
            UserReg.grid(row=8, column=0, sticky='e', pady=20)
            UserBoxReg.grid(row=8, column=1, sticky='w')
            PasswordReg.grid(row=8, column=2, sticky='w', pady=20)
            PassBoxReg.grid(row=8, column=3, sticky='w')
            OkButtonReg.grid(row=9, columnspan=4, ipadx=10, padx=30)

        Label(pop, text="Welcome to LEGARD!", font='Malgun 15 bold', bg='white').grid(row=0, columnspan=4, sticky='ew')
        Button(pop, text="Log In", bg='grey82', fg='black', font='Helvetica 12 bold', width=90, command=ShowLogInEntries)\
            .grid(row=1, columnspan=4, sticky='ew', ipady=20)
        Button(pop, text="Register", bg='brown2', fg='black', font='Helvetica 12 bold', command=ShowRegEntries)\
            .grid(row=5, columnspan=4, sticky='ew', ipady=20)

    def MainScreen(self):
        """
        Set up the main screen after a successful login.
        Creates a new Toplevel window with a Notebook of tabs.
        """
        root = Toplevel(pop)
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.geometry("%dx%d" % (width, height))
        root.title('Main Screen')

        ###############################
        # GPIO Setup and Global Vars  #
        ###############################
        # Define button pins
        ButtonPins = {
            'button1': 14,
            'button2': 15,
            'button3': 18,
            'button4': 23,
            'button5': 24,
            'button6': 25,
            'button7': 8,
            'button8': 7,
            'button9': 1,
            'button10': 12
        }
        GPIO.setmode(GPIO.BCM)
        for pin in ButtonPins.values():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        global Lswitch, MaxStretch
        Lswitch = 0
        MaxStretch = 0

        ###############################
        # Define Button Callback Functions for Tab2
        ###############################
        def button(channel):
            global Lswitch, MaxStretch
            Lswitch = 1
            if Lswitch > MaxStretch:
                MaxStretch = Lswitch
            Label(tab2, text=" ", bg='SpringGreen3', fg='white', font='Helvetica 20', height=1, width=10)\
                .grid(row=9, column=1)

        def button2(channel):
            global Lswitch, MaxStretch
            Lswitch = 2
            if Lswitch > MaxStretch:
                MaxStretch = Lswitch
            Label(tab2, text=" ", bg='SpringGreen3', fg='white', font='Helvetica 20', height=1, width=10)\
                .grid(row=8, column=1)

        def button3(channel):
            global Lswitch, MaxStretch
            Lswitch = 3
            if Lswitch > MaxStretch:
                MaxStretch = Lswitch
            Label(tab2, text=" ", bg='SpringGreen3', fg='white', font='Helvetica 20', height=1, width=10)\
                .grid(row=7, column=1)

        def button4(channel):
            global Lswitch, MaxStretch
            Lswitch = 4
            if Lswitch > MaxStretch:
                MaxStretch = Lswitch
            Label(tab2, text=" ", bg='SpringGreen3', fg='white', font='Helvetica 20', height=1, width=10)\
                .grid(row=6, column=1)

        def button5(channel):
            global Lswitch, MaxStretch
            Lswitch = 5
            if Lswitch > MaxStretch:
                MaxStretch = Lswitch
            Label(tab2, text=" ", bg='SpringGreen3', fg='white', font='Helvetica 20', height=1, width=10)\
                .grid(row=5, column=1)

        def button6(channel):
            global Lswitch, MaxStretch
            Lswitch = 6
            if Lswitch > MaxStretch:
                MaxStretch = Lswitch
            Label(tab2, text=" ", bg='SpringGreen3', fg='white', font='Helvetica 20', height=1, width=10)\
                .grid(row=4, column=1)

        def button7(channel):
            global Lswitch, MaxStretch
            Lswitch = 7
            if Lswitch > MaxStretch:
                MaxStretch = Lswitch
            Label(tab2, text=" ", bg='SpringGreen3', fg='white', font='Helvetica 20', height=1, width=10)\
                .grid(row=3, column=1)

        def button8(channel):
            global Lswitch, MaxStretch
            Lswitch = 8
            if Lswitch > MaxStretch:
                MaxStretch = Lswitch
            Label(tab2, text=" ", bg='SpringGreen3', fg='white', font='Helvetica 20', height=1, width=10)\
                .grid(row=2, column=1)

        def button9(channel):
            global Lswitch, MaxStretch
            Lswitch = 9
            if Lswitch > MaxStretch:
                MaxStretch = Lswitch
            Label(tab2, text=" ", bg='SpringGreen3', fg='white', font='Helvetica 20', height=1, width=10)\
                .grid(row=1, column=1)

        def button10(channel):
            global Lswitch, MaxStretch
            Lswitch = 10
            if Lswitch > MaxStretch:
                MaxStretch = Lswitch
            Label(tab2, text=" ", bg='SpringGreen3', fg='white', font='Helvetica 20', height=1, width=10)\
                .grid(row=0, column=1)

        GPIO.add_event_detect(ButtonPins['button1'], GPIO.RISING, callback=button)
        GPIO.add_event_detect(ButtonPins['button2'], GPIO.RISING, callback=button2)
        GPIO.add_event_detect(ButtonPins['button3'], GPIO.RISING, callback=button3)
        GPIO.add_event_detect(ButtonPins['button4'], GPIO.RISING, callback=button4)
        GPIO.add_event_detect(ButtonPins['button5'], GPIO.RISING, callback=button5)
        GPIO.add_event_detect(ButtonPins['button6'], GPIO.RISING, callback=button6)
        GPIO.add_event_detect(ButtonPins['button7'], GPIO.RISING, callback=button7)
        GPIO.add_event_detect(ButtonPins['button8'], GPIO.RISING, callback=button8)
        GPIO.add_event_detect(ButtonPins['button9'], GPIO.RISING, callback=button9)
        GPIO.add_event_detect(ButtonPins['button10'], GPIO.RISING, callback=button10)

        ###############################
        # Read User Data and Setup    #
        ###############################
        user = []
        df = pd.DataFrame(columns=['Day', 'Value'])
        with open("Users/" + self.query.get() + "/info.txt", "r") as file:
            for i, f in enumerate(file):
                if i == 0:
                    user.append(f.split())
                else:
                    line = f.split()
                    df = df.append({'Day': line[0], 'Value': [int(line[1]), int(line[2]), int(line[3])]}, ignore_index=True)
            day = len(df) + 1

        ###############################
        # Create Notebook and Tabs    #
        ###############################
        tabsystem = ttk.Notebook(root)
        tab1 = Frame(tabsystem)
        tab2 = Frame(tabsystem)
        tab3 = Frame(tabsystem)
        tab4 = Frame(tabsystem)
        tabsystem.add(tab1, text='User Info')
        tabsystem.add(tab2, text='Start Routine')
        tabsystem.add(tab3, text='Check History')
        tabsystem.add(tab4, text='Analitics')
        tabsystem.pack(expand=1, fill="both")

        ###############################
        # TAB 1: User Info and Polar Plot
        ###############################
        self.tkpic = ImageTk.PhotoImage(
            Image.open("/home/si/Desktop/LEGARD/app/prof_pic.png").resize((200, 200))
        )
        Label(tab1, image=self.tkpic).grid(rowspan=3, column=0)
        fig = Figure(figsize=(3, 2), dpi=100)
        fig.patch.set_facecolor('#E0E0E0')
        ax = fig.add_subplot(111, polar=True)
        ax.axis('off')
        canvas = FigureCanvasTkAgg(fig, master=tab1)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=2, sticky="E")

        # Compute values for polar plot if data exists
        upperLimit = 100
        lowerLimit = 30
        DfVal1, DfVal2, DfVal3 = [], [], []
        if len(df) != 0:
            max1 = 0
            for f in df['Value']:
                DfVal1.append(f[0])
                DfVal2.append(f[1])
                DfVal3.append(f[2])
                if f[0] > max1:
                    max1 = f[0]
            slope = (max1 - lowerLimit) / max1
            heights = [slope * val + lowerLimit for val in DfVal1]
            width = 2 * np.pi / len(df.index)
            indexes = list(range(1, len(df.index) + 1))
            angles = [element * width for element in indexes]
            bars = ax.bar(
                x=angles,
                height=heights,
                width=width,
                bottom=lowerLimit,
                linewidth=2,
                edgecolor="black",
                color="#61a4b2"
            )
            labelPadding = 4
            for bar, angle, height, label, value in zip(bars, angles, heights, df["Day"], DfVal1):
                rotation = np.rad2deg(angle)
                if angle >= np.pi/2 and angle < 3*np.pi/2:
                    alignment = "right"
                    rotation = rotation + 180
                else:
                    alignment = "left"
                ax.text(
                    x=angle,
                    y=lowerLimit + bar.get_height() + labelPadding,
                    s=str(value),
                    ha=alignment,
                    va='center',
                    rotation=rotation,
                    rotation_mode="anchor"
                )
        Label(tab1, text="Name: " + str(user[0][0]) + " " + str(user[0][1]), font='Helvetica 20')\
            .grid(row=0, column=1, padx=20, pady=40, sticky="W")
        Label(tab1, text="User: " + str(user[0][3]), font='Helvetica 20')\
            .grid(row=0, column=2, padx=20, pady=40, sticky="W")
        Label(tab1, text="Gender: " + str(user[0][2]), font='Helvetica 20')\
            .grid(row=1, column=1, padx=20, sticky="W")

        ###############################
        # TAB 2: Start Routine        #
        ###############################
        Label(tab2, text="Stretch your leg the \n highest you can. Then,\n click Start.", font='Helvetica 20')\
            .grid(rowspan=5, column=0, padx=100)

        def Start():
            GPIO.setmode(GPIO.BCM)
            # Remove GPIO events for all pins
            for pin in ButtonPins.values():
                GPIO.remove_event_detect(pin)
            bus = smbus.SMBus(1)
            self.Start2(user, day, MaxStretch)

        Button(tab2, text="Start", bg='SpringGreen3', fg='white', font='Helvetica 20',
               width=10, height=5, command=Start).grid(rowspan=5, column=0)
        # Create placeholder labels for button events
        for i in range(10):
            Label(tab2, text=" ", bg='grey40', fg='white', font='Helvetica 20', height=1, width=10)\
                .grid(row=i, column=1, pady=2)

        ###############################
        # TAB 3: Check History        #
        ###############################
        path = "/home/si/Desktop/LEGARD/app/Users/" + str(user[0][3])
        dir_list = os.listdir(path)

        def show():
            try:
                label.config(text="Viewing " + clicked.get())
                with open(path + "/" + str(clicked.get())) as f:
                    lines = f.readlines()
                line2 = [line.strip().split("\t") for line in lines]
                found_time_series = False
                found_coords = False
                X, Y, Y2 = [], [], []
                V, MxAng1, T = [], [], []
                coordinates = []
                for i, row in enumerate(line2):
                    if not row or row == ['']:
                        continue
                    if "X(Time)" in row[0] and not found_time_series:
                        found_time_series = True
                        continue
                    if row[0].startswith("X Cord"):
                        found_coords = True
                        continue
                    if found_time_series and not found_coords:
                        try:
                            X.append(int(row[0]))
                            if len(row) == 2:
                                Y.append(float(row[1]))
                            elif len(row) == 3:
                                Y.append(float(row[1]))
                                Y2.append(float(row[2].replace("\n", "")))
                        except Exception as e:
                            continue
                    if found_coords:
                        try:
                            if len(row) == 1:
                                parts = row[0].split(",")
                                if len(parts) == 2:
                                    x_val = int(parts[0].strip())
                                    y_val = int(parts[1].strip())
                                    coordinates.append((x_val, y_val))
                            elif len(row) >= 2:
                                x_val = int(row[0].strip())
                                y_val = int(row[1].strip())
                                coordinates.append((x_val, y_val))
                        except Exception as e:
                            continue
                    if not found_time_series and not found_coords:
                        if i != 0:
                            try:
                                MxAng1.append(row[1].strip('][').split(', '))
                                V.append(row[2].strip('][').split(', '))
                                T.append(row[3].strip('][').split(', '))
                            except Exception as e:
                                continue
                global lenX
                lenX = len(X)
                bx.cla()
                bx.plot(X, Y, color='b')
                if Y2:
                    bx.plot(X, Y2, color='r')
                for i, t in enumerate(T):
                    bx.text(float(t[1]) + 0.5, float(max(Y)) + 7, 'Rep ' + str(i + 1))
                    bx.text(float(t[1]) + 0.5, float(max(Y)) + 5, 'Max. Angle ' + str(MxAng1[i][0]))
                    bx.text(float(t[1]) + 0.5, float(max(Y)) + 1, 'Max. Vel. ' + max(V[i]))
                    bx.axvline(x=float(t[1]), color='b', linestyle="dashed")
                    bx.axvline(x=float(t[-1]) + 2, color='b', linestyle="dashed")
                update(1)
                if coordinates:
                    x_coords, y_coords = zip(*coordinates)
                    heatmap, x_edges, y_edges = np.histogram2d(
                        x_coords, y_coords, bins=(101, 101), range=[[-50, 50], [-50, 50]]
                    )
                    average_x = np.mean(x_coords)
                    average_y = np.mean(y_coords)
                    # Update the placeholder empty heat map
                    ax_heat.cla()
                    im = ax_heat.imshow(
                        heatmap.T, origin='lower', cmap='viridis', interpolation='nearest',
                        extent=[-50, 50, -50, 50]
                    )
                    fig_heat.colorbar(im, ax=ax_heat, label='Frequency')
                    ax_heat.set_title('Weight Distribution')
                    ax_heat.set_xlabel('X-axis')
                    ax_heat.set_ylabel('Y-axis')
                    ax_heat.grid(color='white', linestyle='--', linewidth=0.5)
                    ax_heat.scatter(average_x, average_y, color='red', s=100, marker='o', label='Average Point')
                    ax_heat.legend()
                    canvas_heat.draw()
            except Exception as e:
                label.config(text="No Correct Data: " + str(e))

        def update(val):
            pos = s_time.val
            bx.axis([pos, pos + 10, 0, 30])
            canvas.draw_idle()  # Updated to use the correct canvas variable

        clicked = StringVar()
        clicked.set("Select File to View")
        drop = OptionMenu(tab3, clicked, *dir_list)
        drop.grid(row=0, columnspan=5)
        Button(tab3, text="View", command=show).grid(row=1, columnspan=5)
        label = Label(tab3, text=" ")
        label.grid(row=2, columnspan=5)

        fig_hist = plt.Figure(figsize=(8, 3))
        canvas = FigureCanvasTkAgg(fig_hist, tab3)
        canvas.get_tk_widget().grid(row=3, columnspan=5)
        global bx
        bx = fig_hist.add_subplot(111)
        fig_hist.subplots_adjust(bottom=0.25)
        bx.axis([0, 9, 0, 30])
        bx_time = fig_hist.add_axes([0.12, 0.1, 0.78, 0.03])
        s_time = Slider(bx_time, 'Time', 0, 1000, valinit=0)
        s_time.on_changed(update)

        # Create an empty heat map placeholder (like the top one) until a file is selected
        empty_data = np.zeros((101, 101))
        fig_heat = Figure(figsize=(8, 6))
        ax_heat = fig_heat.add_subplot(111)
        ax_heat.imshow(empty_data, cmap='viridis', interpolation='nearest', extent=[-50, 50, -50, 50])
        ax_heat.set_title('Cartesian Heat Map of Coordinates')
        ax_heat.set_xlabel('X-axis')
        ax_heat.set_ylabel('Y-axis')
        ax_heat.grid(True)
        canvas_heat = FigureCanvasTkAgg(fig_heat, tab3)
        canvas_heat.draw()
        canvas_heat.get_tk_widget().grid(row=4, columnspan=5)

        ###############################
        # TAB 4: Analytics            #
        ###############################
        figtab4 = plt.Figure(figsize=(5, 2))
        canvas = FigureCanvasTkAgg(figtab4, tab4)
        canvas.get_tk_widget().grid(row=1, column=0, pady=10)
        ax_tab4 = figtab4.add_subplot(111)
        ax_tab4.set_ylabel('Repetitions')
        ax_tab4.set_title('Repetitions per Day')
        ax_tab4.plot(df["Day"], DfVal1)
        ax_tab4.tick_params(axis='x', labelrotation=90)

        fig2tab4 = plt.Figure(figsize=(5, 2))
        canvas = FigureCanvasTkAgg(fig2tab4, tab4)
        canvas.get_tk_widget().grid(row=1, column=1, pady=10)
        ax2_tab4 = fig2tab4.add_subplot(111)
        ax2_tab4.set_ylabel('Usage Time')
        ax2_tab4.set_title('Session Length')
        ax2_tab4.bar(df["Day"], DfVal2)
        ax2_tab4.tick_params(axis='x', labelrotation=90)

        fig3tab4 = plt.Figure(figsize=(5, 2))
        canvas = FigureCanvasTkAgg(fig3tab4, tab4)
        canvas.get_tk_widget().grid(row=2, column=1)
        ax3_tab4 = fig3tab4.add_subplot(111)
        ax3_tab4.set_ylabel('Resting Time')
        ax3_tab4.set_title('Resting Time Per Session')
        ax3_tab4.bar(df["Day"], DfVal3)
        ax3_tab4.tick_params(axis='x', labelrotation=90)

    def Start2(self, user, day, MaxStretch):
        """
        Begin the sensor routine and graph display.
        Sets up sensor parameters based on the maximum stretch value,
        configures GPIO and I2C sensors, and starts processes for sensor data collection.
        """
        # Determine sensor settings based on MaxStretch value
        ButtonPin = 14
        lastTnumber = int(MaxStretch)
        global MaxAngle
        if lastTnumber != 0:
            Default = 0
            if lastTnumber in [1, 2]:
                ButtonPin2 = 15
                ButtonPin3 = 18
                MaxAngle = 3.5
            elif lastTnumber == 3:
                ButtonPin2 = 15
                ButtonPin3 = 18
                MaxAngle = 3.5
            elif lastTnumber == 4:
                ButtonPin2 = 18
                ButtonPin3 = 23
                MaxAngle = 6.35
            elif lastTnumber == 5:
                ButtonPin2 = 23
                ButtonPin3 = 24
                MaxAngle = 8.2
            elif lastTnumber == 6:
                ButtonPin2 = 24
                ButtonPin3 = 25
                MaxAngle = 10.54
            elif lastTnumber == 7:
                ButtonPin2 = 25
                ButtonPin3 = 8
                MaxAngle = 13.28
            elif lastTnumber == 8:
                ButtonPin2 = 8
                ButtonPin3 = 7
                MaxAngle = 16.28
            elif lastTnumber == 9:
                ButtonPin2 = 7
                ButtonPin3 = 1
                MaxAngle = 19.24
            elif lastTnumber == 10:
                ButtonPin2 = 1
                ButtonPin3 = 12
                MaxAngle = 21.6
        else:
            Default = 1
            ButtonPin2 = 15
            ButtonPin3 = 18
            MaxAngle = 3.5

        # GPIO and Sensor Setup
        GPIO.setmode(GPIO.BCM)
        for pin in [ButtonPin, ButtonPin2, ButtonPin3]:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        i2c = I2C(1)  # Device is /dev/i2c-1
        sensor = adafruit_bno055.BNO055_I2C(i2c, address=0x28)
        sensor2 = adafruit_bno055.BNO055_I2C(i2c, address=0x29)
        plt.style.use('fivethirtyeight')

        #################################
        # Define Sensor Button Callbacks#
        #################################
        def Ibutton(channel):
            qw2 = sensor2.quaternion[0]
            Rad2Deg = 180 / pi
            if qw2 is None:
                pass
            else:
                try:
                    btn1[11] = round(2 * acos(qw2) * Rad2Deg, 2)
                except:
                    pass

            if btn2[0] != 0 and btn1[1] == False:
                btn2[0] = 0
                btn2[3] = "Keep on good job!"
            elif btn2[0] == 0 and btn1[1] == True and time.time() - btn1[7] > 2 and btn2[2] == False:
                btn2[8] += 1
                if btn2[8] == 3:
                    btn2[2] = True
                    btn2[3] = "Stretch Failure"
                btn2[3] = "Didn't Reach Target, Try Going Higher"

            if btn1[0] == 0 and time.time() - btn1[7] > 0.5:
                if btn2[2] == True and not btn2[4] == 3:
                    btn2[3] = "Wait Until Timer is Over"
                else:
                    if btn2[2] == False:
                        btn1[0] = 1
                        btn1[1] = True
                        btn1[7] = time.time()
            elif btn1[0] == 1 and time.time() - btn1[7] > 0.5:
                btn1[6] += 1
                info.append([btn1[6], btn1[5], btn1[2], btn1[8], btn1[10], btn2[11]])
                print('Repetition\tMax Angle\tAvg. Velocity(cm/s)\tTime\tDistance\n' +
                      str(btn1[6]) + '\t' + str(btn1[5]) + '\t'*2 + str(btn1[2]) + '\t' + str(btn1[8]) + '\t' + str(btn1[10]) + '\n')
                btn1[0] = 0
                btn1[1] = False
                btn1[2] = manager.list([0])
                btn1[3] = 0
                btn1[4] = 0
                btn1[5] = 0
                btn2[11] = 0
                btn2[1] = False
                btn1[7] = time.time()
                btn1[8] = manager.list([0])
                btn1[10] = manager.list([0])
                btn2[6] = 0
                btn2[10] = 0
                btn2[7] = False

        GPIO.add_event_detect(ButtonPin, GPIO.RISING, callback=Ibutton)

        def Fbutton2(channel):
            if btn1[1] == True and btn2[1] == False and btn2[2] == False:
                btn2[8] = 0
                btn2[0] = 1
                btn2[3] = "Good Stretch!"
                btn2[1] = True
                btn2[6] = 0
                btn2[7] = False

        GPIO.add_event_detect(ButtonPin2, GPIO.RISING, callback=Fbutton2)

        #################################
        # Main Window for Sensor Routine#
        #################################
        class MainWindow(Tk):
            def __init__(self):
                Tk.__init__(self)
                self.geometry('1200x900')
                myFont = font.Font(family='Helvetica', size=40, weight='bold')
                # Set up figure and canvas for plotting
                self.fig = Figure(figsize=(11, 6), dpi=50)
                self.plot1 = self.fig.add_subplot(111)
                self.canvas = FigureCanvasTkAgg(self.fig, master=self)
                self.canvas.draw()
                self.canvas.get_tk_widget().grid(row=2, column=0)

                global sets_and_rep, Messages
                sets_and_rep = StringVar(self)
                Messages = StringVar(self)
                sets_and_rep.set("Set: %d Rep: %d TA: %.1f" % (btn2[4], btn1[6], MaxAngle))
                Messages.set(str(btn2[3]))
                self.Rep = Label(self, textvariable=sets_and_rep, font='Helvetica 20')
                self.Mes = Label(self, textvariable=Messages, bg='SpringGreen3', fg='black', font='Helvetica 20', height=2, width=60)
                self.Mes.grid(row=0, columnspan=3)
                self.Rep.grid(row=1, columnspan=3, sticky="W")
                s = ttk.Style()
                s.theme_use('clam')
                s.configure("red.Vertical.TProgressbar", background='red')
                s.configure("yellow.Vertical.TProgressbar", background='yellow')
                s.configure("green.Vertical.TProgressbar", background='green')
                self.PB = ttk.Progressbar(self, orient='vertical', mode='determinate', length=300, maximum=30, style='red.Vertical.TProgressbar')
                self.PB.grid(row=2, column=1, sticky="W")
                self.Stop = Button(self, text="Stop", bg='firebrick1', fg='white', font='Helvetica 20', height=10, width=15, command=self.close)\
                    .grid(row=2, column=2, sticky="W")
                self.ani = FuncAnimation(self.fig, self.plot, interval=20)

            def close(self):
                Box = messagebox.askquestion('Message', "Save Today's Performance?")
                if Box == 'yes':
                    current_time = datetime.datetime.now()
                    current_day = datetime.date.today()
                    today = str(current_day) + '_' + str(current_time.hour) + '_' + str(current_time.minute)
                    with open("Users/" + user[0][3] + "/" + today + ".txt", "a") as f:
                        f.write("Repetition\tMax. Angle Reached1\tAvg. Velocity\tTime\tDistance\tDefault=" + str(Default) +
                                "\tMax Target Angle=" + str(MaxAngle) + "\tMax. Angle Reached2" + "\n")
                        for l in info:
                            f.write(str(l[0]) + "\t" + str(l[1]) + "\t" + str(l[2]) + "\t" + str(l[3]) + "\t" + str(l[4]) + "\t" + str(l[5]) + "\n")
                        f.write("X(Time)\tY(Sensor 1 Angle)\tY(Sensor 2 Angle)\n")
                        for xs, ys, y2s in zip(x, y, y2):
                            f.write(str(xs) + '\t' + str(ys) + '\t' + str(y2s) + '\n')
                    with open("Users/" + user[0][3] + "/info.txt", "a") as file:
                        file.write("Day" + str(day) + '\t' + str(btn1[6]) + '\t' + str(max(x)) + '\t' + str(y.count(0)) + '\n')
                    root.destroy()
                else:
                    root.destroy()
                GPIO.remove_event_detect(ButtonPin)
                GPIO.remove_event_detect(ButtonPin2)
                GPIO.remove_event_detect(ButtonPin3)
                GPIO.cleanup()

            def plot(self, i):
                try:
                    sets_and_rep.set("Set: %d Rep: %d TA: %.1f" % (btn2[4], btn1[6], MaxAngle))
                    Messages.set(str(btn2[3]))
                    self.plot1.set(xlim=(x[-1] - 15, x[-1] + 5), ylim=(-1, 40))
                    self.plot1.set_xlabel('Time (s)')
                    self.plot1.set_ylabel('Angle (Degress)')
                    self.plot1.plot(x, y, color='blue')
                    self.plot1.plot(x, y2, color='red')
                    self.plot1.legend([str(round(y[-1], 2)) + 'deg' + '\n' + str(round(y2[-1], 2)) + 'deg'],
                                      prop={'size': 40}, handletextpad=0, handlelength=0)
                    self.canvas.draw()
                except:
                    pass

        #################################
        # Define Loop and Calculation Functions
        #################################
        def loop():
            root.mainloop()

        def Calculations():
            while True:
                if btn2[2] == False:
                    qw = sensor.quaternion[0]
                    qw2 = sensor2.quaternion[0]
                    r = 126
                    Rad2Deg = 180 / pi
                    while btn1[9] <= 0 or btn1[9] > 100:
                        qw = sensor.quaternion[0]
                        if qw is None:
                            continue
                        else:
                            try:
                                btn1[9] = round(2 * acos(qw) * Rad2Deg, 2)
                            except:
                                pass
                    while btn1[11] <= 0 or btn1[11] > 100:
                        qw2 = sensor2.quaternion[0]
                        if qw2 is None:
                            continue
                        else:
                            try:
                                btn1[11] = round(2 * acos(qw2) * Rad2Deg, 2)
                            except:
                                pass
                    if btn1[0] == 0:
                        a = 0
                        a2 = 0
                        if qw is None:
                            qw = qw1[-1]
                        else:
                            try:
                                _ = round(2 * acos(qw) * Rad2Deg, 2)
                            except:
                                qw = qw1[-1]
                        if qw2 is None:
                            qw2 = qw2_1[-1]
                        else:
                            try:
                                _ = round(2 * acos(qw2) * Rad2Deg, 2)
                            except:
                                qw2 = qw2_1[-1]
                    else:
                        if qw is None:
                            qw = qw1[-1]
                            a = round(2 * acos(qw) * Rad2Deg, 2) - btn1[9]
                        else:
                            try:
                                a = round(2 * acos(qw) * Rad2Deg, 2) - btn1[9]
                            except:
                                qw = qw1[-1]
                                a = round(2 * acos(qw) * Rad2Deg, 2) - btn1[9]
                        if qw2 is None:
                            qw2 = qw2_1[-1]
                            a2 = round(2 * acos(qw2) * Rad2Deg, 2) - btn1[11]
                        else:
                            try:
                                a2 = round(2 * acos(qw2) * Rad2Deg, 2) - btn1[11]
                            except:
                                qw2 = qw2_1[-1]
                                a2 = round(2 * acos(qw2) * Rad2Deg, 2) - btn1[11]
                    qw1.append(qw)
                    qw2_1.append(qw2)
                    y.append(round(a, 2))
                    y2.append(round(a2, 2))
                    x.append(next(index))
                    if btn1[1] == True:
                        if btn1[2][-1] == 0:
                            btn1[3] = x[-1]
                            btn1[4] = x[-1] + 1
                        else:
                            btn1[4] = x[-1]
                        if y[-1] > btn1[5]:
                            btn1[5] = y[-1]
                        if y2[-1] > btn2[11]:
                            btn2[11] = y2[-1]
                        Time = btn1[4] - btn1[3]
                        if Time == 0:
                            v = 0
                        else:
                            v = y[-1] / Time
                        btn2[10] = v
                        btn1[10].append(round(2 * pi * r * (a / 360), 2))
                        btn1[2].append(round(v, 2))
                        btn1[8].append(x[-1])
                        if v <= 0.5 and btn2[0] == 0:
                            if btn2[7] == False:
                                btn2[6] = time.time()
                                btn2[7] = True
                            else:
                                if time.time() - btn2[6] > 4:
                                    btn2[2] = True
                                    btn2[3] = "Stretch Failure"
                                    btn1[7] = time.time()
                                else:
                                    continue
                        else:
                            btn2[6] = 0
                            btn2[7] = False
                    time.sleep(1)
                else:
                    a = 0
                    a2 = 0
                    y.append(round(a, 2))
                    x.append(next(index))
                    y2.append(round(a2, 2))
                    if time.time() - btn1[7] > 1.5 and btn2[5] == False:
                        if btn2[4] == 3:
                            btn2[3] = "Routine Has Ended. Click On Stop"
                        else:
                            btn2[5] = True
                            btn1[7] = time.time()
                            btn2[9] = btn1[6] - btn2[9]
                            btn2[3] = "Return To Home And Rest For " + str(round((btn2[9] * 20) / 60, 2)) + " minutes"
                    elif time.time() - btn1[7] > btn2[9] * 20 and btn2[5] == True:
                        btn2[4] += 1
                        btn2[2] = False
                        btn2[5] = False
                        btn1[7] = time.time()
                        btn2[8] = 0
                        btn2[3] = "Continue"
                    elif time.time() - btn1[7] > 2 and btn2[5] == True:
                        time2Display = btn2[9] * 20 - (time.time() - btn1[7])
                        if time2Display / 60 < 1:
                            minute = 0
                            seconds = int(time2Display % 60)
                        else:
                            minute = int((time2Display - time2Display % 60) / 60)
                            seconds = int(time2Display % 60)
                        btn2[3] = str(minute) + ":" + str(seconds) + " remaining"
                    time.sleep(1)

        ###############################
        # Start Processes for Sensor Routine
        ###############################
        with Manager() as manager:
            index = count()
            x = manager.list([])
            y = manager.list([])
            y2 = manager.list([])
            qw1 = manager.list([0])
            qw2_1 = manager.list([0])
            btn1 = manager.list([0, False, manager.list([0]), 0, 0, 0, 0, time.time(), manager.list([0]), 0, manager.list([0]), 0])
            btn2 = manager.list([0, False, False, "", 1, False, 0, False, 0, 0, 0, 0])
            info = manager.list([])

            root = MainWindow()
            p1 = Process(target=Calculations)
            p2 = Process(target=loop)
            p1.start()
            p2.start()
            p1.join()
            p2.join()

###############################
#        MAIN ENTRY POINT     #
###############################

pop = Tk()
app = Frames()
app.popup(pop)
pop.mainloop()
