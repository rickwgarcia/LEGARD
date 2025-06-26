from tkinter import *
import tkinter.font as font
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tkinter import ttk
from PIL import ImageTk, Image
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk) 
import subprocess
import RPi.GPIO as GPIO

from itertools import count
from matplotlib.animation import FuncAnimation
from multiprocessing import Process, Manager
from tkinter import Tk, Button, Label
from sys import argv
from tkinter import messagebox
import time
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055
from math import *
import datetime
import os

class Frames(object):
                
    def MainScreen(self):
        root = Toplevel(pop)
        width= root.winfo_screenwidth()
        height= root.winfo_screenheight()
        root.geometry("%dx%d" % (width, height))
        root.title('Main Screen')
        
        ButtonPin = 14
        ButtonPin2 = 15
        ButtonPin3 = 18
        ButtonPin4 = 23
        ButtonPin5 = 24
        ButtonPin6 = 25
        ButtonPin7 = 8
        ButtonPin8 = 7
        ButtonPin9 = 1
        ButtonPin10 = 12
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(ButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(ButtonPin2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(ButtonPin3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(ButtonPin4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(ButtonPin5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(ButtonPin6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(ButtonPin7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(ButtonPin8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(ButtonPin9, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(ButtonPin10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        global Lswitch
        global MaxStretch
        Lswitch = 0
        MaxStretch = 0

        def button(channel):
            global Lswitch
            global MaxStretch
            Lswitch = 1
            if Lswitch > MaxStretch:
                MaxStretch = Lswitch
            Label(tab2, text = " ", bg='SpringGreen3', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=9,column=1)
            
        GPIO.add_event_detect(ButtonPin, GPIO.RISING,callback=button)

        def button2(channel):
            global Lswitch
            global MaxStretch
            Lswitch = 2
            if Lswitch > MaxStretch:
                MaxStretch = Lswitch
            Label(tab2, text = " ", bg='SpringGreen3', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=8,column=1)
            
        GPIO.add_event_detect(ButtonPin2, GPIO.RISING,callback=button2)
        
        def button3(channel):
            global Lswitch
            global MaxStretch
            Lswitch = 3
            if Lswitch > MaxStretch:
                MaxStretch = Lswitch
            Label(tab2, text = " ", bg='SpringGreen3', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=7,column=1)
            
        GPIO.add_event_detect(ButtonPin3, GPIO.RISING,callback=button3)
        
        def button4(channel):
            global Lswitch
            global MaxStretch
            Lswitch = 4
            if Lswitch > MaxStretch:
                MaxStretch = Lswitch
            Label(tab2, text = " ", bg='SpringGreen3', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=6,column=1)
            
        GPIO.add_event_detect(ButtonPin4, GPIO.RISING,callback=button4)
        
        def button5(channel):
            global Lswitch
            global MaxStretch
            Lswitch = 5
            if Lswitch > MaxStretch:
                MaxStretch = Lswitch
            Label(tab2, text = " ", bg='SpringGreen3', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=5,column=1)
            
        GPIO.add_event_detect(ButtonPin5, GPIO.RISING,callback=button5)
        
        def button6(channel):
            global Lswitch
            global MaxStretch
            Lswitch = 6
            if Lswitch > MaxStretch:
                MaxStretch = Lswitch
            Label(tab2, text = " ", bg='SpringGreen3', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=4,column=1)
            
        GPIO.add_event_detect(ButtonPin6, GPIO.RISING,callback=button6)

        def button7(channel):
            global Lswitch
            global MaxStretch
            Lswitch = 7
            if Lswitch > MaxStretch:
                MaxStretch = Lswitch
            Label(tab2, text = " ", bg='SpringGreen3', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=3,column=1)
            
        GPIO.add_event_detect(ButtonPin7, GPIO.RISING,callback=button7)
        
        def button8(channel):
            global Lswitch
            global MaxStretch
            Lswitch = 8
            if Lswitch > MaxStretch:
                MaxStretch = Lswitch
            Label(tab2, text = " ", bg='SpringGreen3', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=2,column=1)
            
        GPIO.add_event_detect(ButtonPin8, GPIO.RISING,callback=button8)
        
        def button9(channel):
            global Lswitch
            global MaxStretch
            Lswitch = 9
            if Lswitch > MaxStretch:
                MaxStretch = Lswitch
            Label(tab2, text = " ", bg='SpringGreen3', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=1,column=1)
            
        GPIO.add_event_detect(ButtonPin9, GPIO.RISING,callback=button9)
        
        def button10(channel):
            global Lswitch
            global MaxStretch
            Lswitch = 10
            if Lswitch > MaxStretch:
                MaxStretch = Lswitch
            Label(tab2, text = " ", bg='SpringGreen3', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=0,column=1)
            
        GPIO.add_event_detect(ButtonPin10, GPIO.RISING,callback=button10)
        
        user = []
        df = pd.DataFrame(columns=['Day','Value'])
        with open("Users/"+ self.query.get()+"/info.txt","r") as file:
            for i, f in enumerate(file):
                if i == 0:
                    user.append(f.split())
                else:
                    line = f.split()
                    df = df.append({'Day': line[0], 'Value': int(line[1])}, ignore_index=True)
            day = len(df) + 1
                
        tabsystem = ttk.Notebook(root)

        # Create new tabs using Frame widget
        tab1 = Frame(tabsystem)
        tab2 = Frame(tabsystem)

        tabsystem.add(tab1, text='User Info')
        tabsystem.add(tab2, text='Start Routine')
        tabsystem.pack(expand=1, fill="both")
        
        ################################################TAB 1 STUFF############################################################################
        self.tkpic = ImageTk.PhotoImage(Image.open("prof_pic.png").resize((200, 200)))
        Label(tab1, image=self.tkpic).grid(rowspan=3,column=0)
        fig = Figure(figsize=(3,2), dpi = 100)
        fig.patch.set_facecolor('#E0E0E0')
        ax = fig.add_subplot(111, polar=True)
        ax.axis('off')
        canvas = FigureCanvasTkAgg(fig, master = tab1)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1,column=2,sticky="E")
        upperLimit = 100
        lowerLimit = 30

        if len(df) != 0:
            # Compute max and min in the dataset
            max1 = df['Value'].max()

            # Let's compute heights: they are a conversion of each item value in those new coordinates
            # In our example, 0 in the dataset will be converted to the lowerLimit (10)
            # The maximum will be converted to the upperLimit (100)
            slope = (max1 - lowerLimit) / max1
            heights = slope * df.Value + lowerLimit

            # Compute the width of each bar. In total we have 2*Pi = 360°
            width = 2*np.pi / len(df.index)

            # Compute the angle each bar is centered on:
            indexes = list(range(1, len(df.index)+1))
            angles = [element * width for element in indexes]

            # Draw bars
            bars = ax.bar(
                x=angles, 
                height=heights, 
                width=width, 
                bottom=lowerLimit,
                linewidth=2, 
                edgecolor="black",
                color="#61a4b2")

            # little space between the bar and the label
            labelPadding = 4

            # Add labels
            for bar, angle, height, label, value in zip(bars,angles, heights, df["Day"], df["Value"]):

                # Labels are rotated. Rotation must be specified in degrees :(
                rotation = np.rad2deg(angle)

                # Flip some labels upside down
                alignment = ""
                if angle >= np.pi/2 and angle < 3*np.pi/2:
                    alignment = "right"
                    rotation = rotation + 180
                else: 
                    alignment = "left"

                # Finally add the labels
                ax.text(
                    x=angle, 
                    y=lowerLimit + bar.get_height() + labelPadding, 
                    s=str(value), 
                    ha=alignment, 
                    va='center', 
                    rotation=rotation, 
                    rotation_mode="anchor") 
        Label(tab1,text="Name: " + str(user[0][0])+ " "+ str(user[0][1]), font = 'Helvetica 20').grid(row=0,column=1,padx=20,pady=40,sticky="W")
        Label(tab1,text="User: " + str(user[0][2]), font = 'Helvetica 20').grid(row=0,column=2,padx=20,pady=40,sticky="W")
        Label(tab1,text="Gender: " + str(user[0][3]), font = 'Helvetica 20').grid(row=1,column=1,padx=20,sticky="W")
        #Label(tab1,text="Total Repetitions Each Day", font = 'Helvetica 20').grid(row=2,column=1,padx=20)
        
        ################################################TAB 2 STUFF############################################################################ 
        Label(tab2,text="Stretch your leg the \n highest you can. Then,\n click Start.", font = 'Helvetica 20').grid(rowspan=5,column=0,padx=100)
        
        def Start():
            self.Start2(user,day,MaxStretch)
            
        Button(tab2, text="Start", bg='SpringGreen3', fg='white', font = 'Helvetica 20', width = 10, height = 5, command = Start).grid(rowspan=5,column=0)
        
        Label(tab2, text = " ", bg='grey40', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=0,column=1, pady=2)
        Label(tab2, text = " ", bg='grey40', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=1,column=1, pady=2)
        Label(tab2, text = " ", bg='grey40', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=2,column=1, pady=2)
        Label(tab2, text = " ", bg='grey40', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=3,column=1, pady=2)
        Label(tab2, text = " ", bg='grey40', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=4,column=1, pady=2)
        Label(tab2, text = " ", bg='grey40', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=5,column=1, pady=2)
        Label(tab2, text = " ", bg='grey40', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=6,column=1, pady=2)
        Label(tab2, text = " ", bg='grey40', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=7,column=1, pady=2)
        Label(tab2, text = " ", bg='grey40', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=8,column=1, pady=2)
        Label(tab2, text = " ", bg='grey40', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=9,column=1, pady=2)
        

    def popup(self,pop):
        width= pop.winfo_screenwidth()
        height= pop.winfo_screenheight()
        pop.geometry("%dx%d" % (width, height))
        pop['bg'] = 'white'
        pop.title('Log In')
        self.query = StringVar() #passing parameter via query var
        
        def login(username, password):
            l = []
            NoUser = Label(pop, text = "Credentials Not Found", font = 'Helvetica 10 bold', bg = 'white')
            UserFound = Label(pop, text = "Welcome "+str(username), font = 'Helvetica 10 bold', bg = 'white')
            with open("Users/register.txt", "r") as file:
                for line in file:
                    l.append(line.split())
                for i, credentials in enumerate(l):
                    if username == credentials[0] and password == credentials[1]:
                        NoUser.grid_forget()
                        UserFound.grid(row=10, columnspan=4, sticky='ew',ipady = 20)
                        self.MainScreen()
                        break
                    elif i == len(l)-1:
                        UserFound.grid_forget()
                        NoUser.grid(row=10, columnspan=4, sticky='ew',ipady = 20)
                    else:
                        pass

        def register(first, last, gender, username, password):
            l = []
            add_credentials = 0
            USerExists = Label(pop, text = "Username Already Exists", font = 'Helvetica 10 bold', bg = 'white')
            RegSuccess = Label(pop, text = "Username Registered Succesfully. Proceed to Login", font = 'Helvetica 10 bold', bg = 'white')
            RegNotSuccess = Label(pop, text = "Please Enter Username and Password", font = 'Helvetica 10 bold', bg = 'white')
            with open("Users/register.txt", "r") as file:
                for line in file:
                    l.append(line.split())
                for i, credentials in enumerate(l):
                    if username == "":
                        RegNotSuccess.grid(row=10, columnspan=4, sticky='ew',ipady = 20)
                        add_credentials = 0
                        break
                    elif username == credentials[0]:
                        USerExists.grid(row=10, columnspan=4, sticky='ew',ipady = 20)
                        add_credentials = 0
                        break
                    elif i == len(l)-1 and username != credentials[0] and username != "":
                        add_credentials = 1
                        break
            if add_credentials == 1:
                with open("Users/register.txt", "a") as file:
                    file.write(username+'\t' + password + '\n')
                os.mkdir("Users/"+username) 
                with open("Users/"+username+"/info.txt", "a") as file:
                    file.write(first+'\t'+last+'\t' +gender+'\t' +username+'\t' + password +'\n')
                USerExists.grid_forget()
                RegNotSuccess.grid_forget()
                RegSuccess.grid(row=10, columnspan=4, sticky='ew',ipady = 20)

        User = Label(pop, text = "User: ", font = 'Helvetica 15 bold', bg = 'white')
        User.grid(row=2, column = 0, pady=30)
        UserBox = Entry(pop, font = 'Helvetica 15', textvariable=self.query)
        UserBox.grid(row=2, column = 1)
        
        Password = Label(pop, text = "Password: ", font = 'Helvetica 15 bold', bg = 'white')
        Password.grid(row=3, column = 0)
        PassBox = Entry(pop, font = 'Helvetica 15', show="*")
        PassBox.grid(row=3, column = 1)
        
        def Lbutton():
            u = UserBox.get()
            p = PassBox.get()
            login(u,p)
            UserBox.delete(0, END)
            PassBox.delete(0, END)
        OkButton = Button(pop, text="Log In", bg='SpringGreen3', fg='black', font='Helvetica 10 bold',command = Lbutton)
        OkButton.grid(row=4, column=1,ipadx = 10, ipady = 6, padx = 30)
        ###############################################REGISTER ENTRIES########################################################
        FName = Label(pop, text = "First Name: ", font = 'Helvetica 12 bold', bg = 'white')
        FNameBox = Entry(pop, width = 10,font = 'Helvetica 12')
        
        LName = Label(pop, text = "Last Name: ", font = 'Helvetica 12 bold', bg = 'white')
        LNameBox = Entry(pop, width = 10, font = 'Helvetica 12')
        
        UserReg = Label(pop, text = "User: ", font = 'Helvetica 12 bold', bg = 'white')
        UserBoxReg = Entry(pop, width = 10, font = 'Helvetica 12')
        
        Gender = Label(pop, text = "Gender: ", font = 'Helvetica 12 bold', bg = 'white')
        ma=IntVar()
        fe=IntVar()
        Mcb = Checkbutton(pop, text = "Male", bg = 'white', variable=ma)
        Fcb = Checkbutton(pop, text = "Female", bg = 'white', variable=fe)
        
        PasswordReg = Label(pop, text = "Password: ", font = 'Helvetica 12 bold', bg = 'white')
        PassBoxReg = Entry(pop, width = 10, font = 'Helvetica 12', show="*")  

        def Rbutton():
            NoEntry = Label(pop, text = "Fill All Boxes", font = 'Helvetica 12 bold', bg = 'white')
            f = FNameBox.get()
            l = LNameBox.get()
            u = UserBoxReg.get()
            p = PassBoxReg.get()
            if f == '' or l =='' or u == '' or p == '':
                NoEntry.grid(row=10, columnspan=4, sticky='ew',ipady = 20)
                return
            if fe.get() == 1:
                g = "Female"
            elif ma.get() == 1:
                g = "Male"
            else:
                g = "NotSelected"
                
            register(f,l,g,u,p)
            ma.set(0)
            fe.set(0)
            FNameBox.delete(0, END)
            LNameBox.delete(0, END)
            UserBoxReg.delete(0, END)
            PassBoxReg.delete(0, END)
            return
        
        OkButtonReg = Button(pop, text="Register", bg='SpringGreen3', fg='black', font='Helvetica 10 bold',command = Rbutton)

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
            User.grid(row=2, column = 0, pady=20)
            UserBox.grid(row=2, column = 1)
            Password.grid(row=3, column = 0, pady=20)
            PassBox.grid(row=3, column = 1)
            OkButton.grid(row=4, column=1,ipadx = 10, ipady = 6, padx = 30)
            
        def ShowRegEntries():
            User.grid_forget()
            UserBox.grid_forget()
            Password.grid_forget()
            PassBox.grid_forget()
            OkButton.grid_forget()
            FName.grid(row=6, column = 0, sticky='e',pady=20)
            FNameBox.grid(row=6, column = 1, sticky='w',pady=20)
            LName.grid(row=6, column = 2, sticky='w',pady=20)
            LNameBox.grid(row=6, column = 3, sticky='w',pady=20)
            Gender.grid(row=7, column = 0, sticky='e',pady=20)
            Mcb.grid(row=7, column = 1, sticky='w',pady=20)
            Fcb.grid(row=7, column = 2, sticky='w',pady=20)
            UserReg.grid(row=8, column = 0, sticky='e',pady=20)
            UserBoxReg.grid(row=8, column = 1,sticky='w')
            PasswordReg.grid(row=8, column = 2, sticky='w',pady=20)
            PassBoxReg.grid(row=8, column = 3,sticky='w')
            OkButtonReg.grid(row=9, columnspan=4,ipadx = 10, padx = 30)
        
        Label(pop, text = "Welcome to LEGARD!", font = 'Malgun 15 bold', bg = 'white').grid(row=0, columnspan=4, sticky='ew')
        Button(pop, text="Log In", bg='grey82', fg='black', font='Helvetica 12 bold', width=90, command = ShowLogInEntries).grid(row=1, columnspan=4, sticky='ew',ipady = 20)
        Button(pop, text="Register", bg='brown2', fg='black', font='Helvetica 12 bold',command = ShowRegEntries).grid(row=5, columnspan=4, sticky='ew',ipady = 20)
    
    def Start2(self,user,day,MaxStretch):
        
        GPIO.remove_event_detect(14)
        GPIO.remove_event_detect(15)
        GPIO.remove_event_detect(18)
        GPIO.remove_event_detect(23)
        GPIO.remove_event_detect(24)
        GPIO.remove_event_detect(25)
        GPIO.remove_event_detect(8)
        GPIO.remove_event_detect(7)
        GPIO.remove_event_detect(1)
        GPIO.remove_event_detect(12)
        
        ButtonPin = 14
        lastTnumber = int(MaxStretch)
        global MaxAngle
        if lastTnumber != 0:
            Default = 0
            if lastTnumber == 1 or lastTnumber == 2:
               ButtonPin2 = 15
               MaxAngle = 3.17
            elif lastTnumber == 3:
               ButtonPin2 = 15
               ButtonPin3 = 18
               MaxAngle = 5.8
            elif lastTnumber == 4:
               ButtonPin2 = 18
               ButtonPin3 = 23
               MaxAngle = 7.9
            elif lastTnumber == 5:
               ButtonPin2 = 23
               ButtonPin3 = 24
               MaxAngle = 10.3
            elif lastTnumber == 6:
               ButtonPin2 = 24
               ButtonPin3 = 25
               MaxAngle = 13.4
            elif lastTnumber == 7:
               ButtonPin2 = 25
               ButtonPin3 = 8
               MaxAngle = 16.0
            elif lastTnumber == 8:
               ButtonPin2 = 8
               ButtonPin3 = 7
               MaxAngle = 19.6
            elif lastTnumber == 9:
               ButtonPin2 = 7
               ButtonPin3 = 1
               MaxAngle = 22.0
            elif lastTnumber == 10:
               ButtonPin2 = 1
               ButtonPin3 = 12
               MaxAngle = 25.2
        else:
            Default = 1
            ButtonPin2 = 1
            ButtonPin3 = 12
            MaxAngle = 25.2
            
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(ButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(ButtonPin2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(ButtonPin3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        i2c = I2C(1)  # Device is /dev/i2c-1
        sensor = adafruit_bno055.BNO055_I2C(i2c)
        plt.style.use('fivethirtyeight')

        def Ibutton(channel):
            if btn2[0] != 0 and btn1[1] == False:
                print('Keep on good job!')
                btn2[0] = 0
                btn2[3] = 1
                    
            elif btn2[0] == 0 and btn1[1] == True and time.time()-btn1[7]>2: # and btn2[7] == False
                print("Didn't Reach Target, Try Going Higher")
                btn2[8] += 1
                if btn2[8] == 3:
                    btn2[2] = True
                    btn2[3] = 2
                btn2[3] = 8
                
            if btn1[0] == 0 and time.time()-btn1[7]>0.5:
                if btn2[2] == True:
                    btn2[3] = 4
                else:
                    btn1[0] = 1
                    btn1[1] = True
                    btn1[7] = time.time()
                
            elif btn1[0] == 1 and time.time()-btn1[7]>1.5:
                btn1[6] += 1
                info.append([btn1[6],btn1[5],btn1[2],btn1[8],btn1[10]])
                print('Repetition\tMax Angle\tAvg. Velocity(cm/s)\tTime\tDistance\n'+str(btn1[6])+'\t'+str(btn1[5])+'\t'*2+str(btn1[2])+'\t'+str(btn1[8])+'\t'+str(btn1[10])+'\n')
                btn1[0] = 0
                btn1[1] = False
                btn1[2] = manager.list([0])
                btn1[3] = 0
                btn1[4] = 0
                btn1[5] = 0
                btn2[1] = False
                btn1[7] = time.time()
                btn1[8] = manager.list([0])
                btn1[10] = manager.list([0])
                btn2[6] = 0
                btn2[7] = False
                
        GPIO.add_event_detect(ButtonPin, GPIO.RISING,callback=Ibutton)

        def Fbutton2(channel):
            if btn1[1] == True and btn2[1] == False and btn2[2] == False:
                print('Good Stretch!\n')
                btn2[8] = 0
                btn2[0] = 1
                btn2[3] = 3
                btn2[1] = True
                btn2[6] = 0
                btn2[7] = False
            
        GPIO.add_event_detect(ButtonPin2, GPIO.RISING,callback=Fbutton2)

        class MainWindow(Tk):
            def __init__(self):
                Tk.__init__(self)
                self.geometry('1200x900')
                myFont = font.Font(family='Helvetica', size=25, weight='bold')

                # the figure that will contain the plot
                self.fig = Figure(figsize = (11, 6), dpi = 50)
                self.plot1 = self.fig.add_subplot(111)
                self.canvas = FigureCanvasTkAgg(self.fig, master = self)
                self.canvas.draw()
                self.canvas.get_tk_widget().grid(row=2,column=0)
                
                global sets_and_rep
                sets_and_rep = StringVar(self)
                sets_and_rep.set("Set: %d Rep: %d TA: %.1f" % (btn2[4], btn1[6], MaxAngle))
                self.Rep = Label(self, textvariable = sets_and_rep, font = 'Helvetica 20')
                
                ##################### MESSAGES TO DISPLAY ####################
                self.Mes1 = Label(self, text = " ", bg='SpringGreen3', fg='black', font = 'Helvetica 20', height = 2, width=60)
                self.Mes2 = Label(self, text = "Keep on Good Job!", bg='SpringGreen3', fg='black', font = 'Helvetica 20', height = 2, width=60)
                self.Mes3 = Label(self, text = "Stretch Failure", bg='SpringGreen3', fg='black', font = 'Helvetica 20', height = 2, width=60)
                self.Mes4 = Label(self, text = "Good Stretch!", bg='SpringGreen3', fg='black', font = 'Helvetica 20', height = 2, width=60)
                self.Mes5 = Label(self, text = "Wait Until Timer is Over", bg='SpringGreen3', fg='black', font = 'Helvetica 20', height = 2, width=60)
                self.Mes6 = Label(self, text = "Return to Home and Rest for 2 Minutes", bg='SpringGreen3', fg='black', font = 'Helvetica 20', height = 2, width=60)
                self.Mes7 = Label(self, text = "Continue", bg='SpringGreen3', fg='black', font = 'Helvetica 20', height = 2, width=60)
                self.Mes8 = Label(self, text = "Routine Has Ended Click on Stop", bg='SpringGreen3', fg='black', font = 'Helvetica 20', height = 2, width=60)
                self.Mes9 = Label(self, text = "Didn't Reach Target, Try Going Higher", bg='SpringGreen3', fg='black', font = 'Helvetica 20', height = 2, width=60)
                self.Mes1.grid(row=0,columnspan=3)
                self.Rep.grid(row=1,column=1, sticky = "W") #user[0][0]<---Used to get user info
                
                self.Stop = Button(self, text="Stop", bg='firebrick1', fg='white', font=myFont, height = 5, width=10, command=self.close).grid(row=2,column=1, sticky = "W")
                self.ani = FuncAnimation(self.fig, self.plot, interval = 20)
            
            def close(self):
                Box = messagebox.askquestion('Message', "Save Today's Performance?")
                if Box == 'yes':
                    current_time = datetime.datetime.now()
                    current_day = datetime.date.today()
                    today = str(current_day) + '_' +str(current_time.hour) + '_' + str(current_time.minute)
                    
                    with open("Users/"+user[0][2]+"/"+today+".txt", "a") as f:
                        f.write("Repetition\tMax. Angle Reached\tAvg. Velocity\tTime\tDistance\tDefault="+str(Default)+"\tMax Target Angle="+str(MaxAngle)+"\n")
                        for l in info:
                            f.write(str(l[0])+"\t"+str(l[1])+"\t"+str(l[2])+"\t"+str(l[3])+"\t"+str(l[4])+"\n")
                        f.write("X(Time)\tY(Angle)\n")
                        for xs,ys in zip(x,y):
                            f.write(str(xs)+'\t' + str(ys)+'\n')
                            
                    with open("Users/"+user[0][2]+"/info.txt", "a") as file:
                            file.write("Day"+str(day)+'\t'+str(btn1[6])+'\n')
                            
                    root.destroy()
                    
                elif Box == 'no':
                    root.destroy()
                else:
                    root.destroy()
                
                GPIO.remove_event_detect(14)
                GPIO.remove_event_detect(15)
                GPIO.remove_event_detect(18)
                GPIO.remove_event_detect(23)
                GPIO.remove_event_detect(24)
                GPIO.remove_event_detect(25)
                GPIO.remove_event_detect(8)
                GPIO.remove_event_detect(7)
                GPIO.remove_event_detect(1)
                GPIO.remove_event_detect(12)
                
            def plot(self,i):
                try:
                    if btn2[3] != 0:
                        self.PackLabel()
                    self.plot1.set(xlim =(x[-1]-15, x[-1]+5), ylim =(-1, 40))
                    self.plot1.set_xlabel('Time (s)')
                    self.plot1.set_ylabel('Angle (Degress)')
                    self.plot1.plot(x,y, color='blue')
                    self.plot1.legend([str(round(btn1[2][-1], 2)) + 'cm/s'], prop={'size':40}, handletextpad=0, handlelength =0)
                    self.canvas.draw()
                    
                except:
                    self.plot(1)
                    
            def PackLabel(self):
                sets_and_rep.set("Set: %d Rep: %d TA: %.1f" % (btn2[4], btn1[6], MaxAngle))
                if btn2[3] == 1:
                    self.Mes1.grid_forget()
                    self.Mes3.grid_forget()
                    self.Mes4.grid_forget()
                    self.Mes5.grid_forget()
                    self.Mes6.grid_forget()
                    self.Mes7.grid_forget()
                    self.Mes8.grid_forget()
                    self.Mes9.grid_forget()
                    self.Mes2.grid(row=0,columnspan=3)
                elif btn2[3] == 2:
                    self.Mes1.grid_forget()
                    self.Mes2.grid_forget()
                    self.Mes4.grid_forget()
                    self.Mes5.grid_forget()
                    self.Mes6.grid_forget()
                    self.Mes7.grid_forget()
                    self.Mes8.grid_forget()
                    self.Mes9.grid_forget()
                    self.Mes3.grid(row=0,columnspan=3)
                elif btn2[3] == 3:
                    self.Mes1.grid_forget()
                    self.Mes2.grid_forget()
                    self.Mes3.grid_forget()
                    self.Mes5.grid_forget()
                    self.Mes6.grid_forget()
                    self.Mes7.grid_forget()
                    self.Mes8.grid_forget()
                    self.Mes9.grid_forget()
                    self.Mes4.grid(row=0,columnspan=3)
                elif btn2[3] == 4:
                    self.Mes1.grid_forget()
                    self.Mes2.grid_forget()
                    self.Mes3.grid_forget()
                    self.Mes4.grid_forget()
                    self.Mes6.grid_forget()
                    self.Mes7.grid_forget()
                    self.Mes8.grid_forget()
                    self.Mes9.grid_forget()
                    self.Mes5.grid(row=0,columnspan=3)
                elif btn2[3] == 5:
                    self.Mes1.grid_forget()
                    self.Mes2.grid_forget()
                    self.Mes3.grid_forget()
                    self.Mes4.grid_forget()
                    self.Mes5.grid_forget()
                    self.Mes7.grid_forget()
                    self.Mes8.grid_forget()
                    self.Mes9.grid_forget()
                    self.Mes6.grid(row=0,columnspan=3)
                elif btn2[3] == 6:
                    self.Mes1.grid_forget()
                    self.Mes2.grid_forget()
                    self.Mes3.grid_forget()
                    self.Mes4.grid_forget()
                    self.Mes5.grid_forget()
                    self.Mes6.grid_forget()
                    self.Mes8.grid_forget()
                    self.Mes9.grid_forget()
                    self.Mes7.grid(row=0,columnspan=3)
                elif btn2[3] == 7:
                    self.Mes1.grid_forget()
                    self.Mes2.grid_forget()
                    self.Mes3.grid_forget()
                    self.Mes4.grid_forget()
                    self.Mes5.grid_forget()
                    self.Mes6.grid_forget()
                    self.Mes7.grid_forget()
                    self.Mes9.grid_forget()
                    self.Mes8.grid(row=0,columnspan=3)
                elif btn2[3] == 8:
                    self.Mes1.grid_forget()
                    self.Mes2.grid_forget()
                    self.Mes3.grid_forget()
                    self.Mes4.grid_forget()
                    self.Mes5.grid_forget()
                    self.Mes6.grid_forget()
                    self.Mes7.grid_forget()
                    self.Mes8.grid_forget()
                    self.Mes9.grid(row=0,columnspan=3)
                return

        def loop():
            root.mainloop()
            
        def Calculations():
            while True:
                if btn2[2] == False:
                    qw = sensor.quaternion[0]
                    r = 126
                    while btn1[9] <= 0 or btn1[9] >100:
                        qw = sensor.quaternion[0]
                        if qw is None:
                            continue
                        else:
                            btn1[9] = round(2*acos(qw)*57.2957795131, 2)
                    try:
                        if btn1[0] == 0:
                            a=0
                        else:
                            a = round(2*acos(qw)*57.2957795131, 2) - btn1[9]
                        qw1.append(qw)
                        y.append(round(a, 2))
                        x.append(next(index))
                        time.sleep(1)
                    except:
                        qw = qw1[-1]
                        if btn1[0] == 0:
                            a=0
                        else:
                            try:
                                a = round(2*acos(qw)*57.2957795131, 2) - btn1[9]
                                qw1.append(qw1[-1])
                            except:
                                a = round(2*acos(qw1[-2])*57.2957795131, 2) - btn1[9]
                                qw1.append(qw1[-2])
                        y.append(round(a, 2))
                        x.append(next(index))
                        time.sleep(1)
                    if btn1[1] == True:
                        if btn1[2][-1] == 0:
                            btn1[3] = x[-1] #init. time
                            btn1[4] = x[-1] + 1 # final time
                        else:
                            btn1[4] = x[-1]
                            
                        if y[-1] > btn1[5]:
                            btn1[5] = y[-1]
                        try:
                            v = (btn1[10][-1] - btn1[10][-2]) / (btn1[4]-btn1[3])
                        except:
                            v = (btn1[10][-1]) / (btn1[4]-btn1[3])
                            
                        btn1[10].append(round(2*pi*r*(a/360), 2))
                        btn1[2].append(round(v,2))
                        btn1[8].append(x[-1])
                        
                        if v <= 0.5 and btn2[0] == 0:
                            if btn2[7] == False:
                                btn2[6] = time.time()
                                btn2[7] = True
                            else:
                                if time.time()-btn2[6]>5:
                                    btn2[2] = True
                                    btn2[3] = 2
                                    btn1[7] = time.time()
                                else:
                                    continue
                        else:
                            btn2[6] = 0
                            btn2[7] = False
                else:
                    a = 0
                    y.append(round(a, 2))
                    x.append(next(index))
                    if time.time()-btn1[7]>1.5 and btn2[5] == False: #Used to display messages
                        if btn2[4] == 3:
                            btn2[3] = 7
                        else:
                            btn2[3] = 5
                            btn2[5] = True
                            btn1[7] = time.time()
                    elif time.time()-btn1[7]>120 and btn2[5] == True:#This will reset the system to continue
                        btn2[4] += 1
                        btn2[2] = False
                        btn2[5] = False
                        btn1[7] = time.time()
                        btn2[8] = 0
                        btn2[3] = 6
                    
                    time.sleep(1)
                    
        if __name__ == '__main__':
            with Manager() as manager:
                index = count()
                x = manager.list([])
                y = manager.list([])
                qw1 = manager.list([0])
                ####################[clicked, false/ true when clicked, velocity values, init. time, final time, max angle, repetition, time when clicked, init. rot angle, angle Values]
                btn1 = manager.list([0, False, manager.list([0]), 0, 0, 0, 0, time.time(), manager.list([0]), 0, manager.list([0])])
                ####################[clicked and # cycles to display "keep on good job", Used to detect when reached goal, stop workout, value for messages, # set, check point to display message, set timer when velocity = 0, check point for vel timer, bit used to know if streatch failure has reached 3 times]
                btn2 = manager.list([0, False, False, 0, 1, False, 0, False, 0])
                info = manager.list([])
                
                root = MainWindow()
                p1 = Process(target = Calculations)
                p2 = Process(target = loop)
                p1.start()
                p2.start()
                p1.join()
                p2.join()
        
pop = Tk()
app = Frames()
app.popup(pop)
pop.mainloop()

