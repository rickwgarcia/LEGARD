from tkinter import *
import tkinter.font as font
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
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
from tkinter import Tk, Button, Label, ttk
from sys import argv
from tkinter import messagebox
import time
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055
from math import *
import datetime
import os
import smbus

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
                    df = df.append({'Day': line[0], 'Value': [int(line[1]), int(line[2]), int(line[3])]}, ignore_index=True)
            day = len(df) + 1
                
        tabsystem = ttk.Notebook(root)

        # Create new tabs using Frame widget
        tab1 = Frame(tabsystem)
        tab2 = Frame(tabsystem)
        tab3 = Frame(tabsystem)
        tab4 = Frame(tabsystem)

        tabsystem.add(tab1, text='User Info')
        tabsystem.add(tab2, text='Start Routine')
        tabsystem.add(tab3, text='Check History')
        tabsystem.add(tab4, text='Analitics')
        tabsystem.pack(expand=1, fill="both")
        
        ################################################TAB 1 STUFF############################################################################
        self.tkpic = ImageTk.PhotoImage(Image.open("/home/si/Desktop/LEGARD/app/prof_pic.png").resize((200, 200)))
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
        DfVal1 = []
        DfVal2 = []
        DfVal3 = []
        
        if len(df) != 0:
            # Compute max and min in the dataset
            max1 = 0
            for f in df['Value']:
                DfVal1.append(f[0]) #Repetitions
                DfVal2.append(f[1]) #Max Usage Time
                DfVal3.append(f[2]) #Resting Time
                if f[0] > max1:
                    max1 = f[0]  

            # Let's compute heights: they are a conversion of each item value in those new coordinates
            # In our example, 0 in the dataset will be converted to the lowerLimit (10)
            # The maximum will be converted to the upperLimit (100)
            slope = (max1 - lowerLimit) / max1
            heights = [slope * val + lowerLimit for val in DfVal1]

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
            for bar, angle, height, label, value in zip(bars,angles, heights, df["Day"], DfVal1):

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
        Label(tab1,text="User: " + str(user[0][3]), font = 'Helvetica 20').grid(row=0,column=2,padx=20,pady=40,sticky="W")
        Label(tab1,text="Gender: " + str(user[0][2]), font = 'Helvetica 20').grid(row=1,column=1,padx=20,sticky="W")
        #Label(tab1,text="Total Repetitions Each Day", font = 'Helvetica 20').grid(row=2,column=1,padx=20)
        
        ################################################TAB 2 STUFF############################################################################ 
        Label(tab2,text="Stretch your leg the \n highest you can. Then,\n click Start.", font = 'Helvetica 20').grid(rowspan=5,column=0,padx=100)
        
        def Start():
            GPIO.setmode(GPIO.BCM)
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
            bus = smbus.SMBus(1)
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
 
         ################################################TAB 3 STUFF############################################################################ 
        path = "/home/si/Desktop/LEGARD/app/Users/" + str(user[0][3])
        dir_list = os.listdir(path)
        
        # Change the label text
        def show():
            try:
                label.config( text = "Viewing " + clicked.get() )
                with open(path + "/" + str(clicked.get())) as f:
                    line2 = [line.split("\t") for line in f]
                found = False
                X = []
                Y = []
                Y2 = []
                V = []
                MxAng1 = []
                MxAng2 = []
                T = []
                
                bx.cla()
                for i, tst in enumerate(line2):
                    if "X(Time)" in tst and found == False:
                        found = True
                    elif found == True:
                        X.append(int(tst[0]))
                        if len(tst) == 3:
                            Y.append(float(tst[1]))
                            Y2.append(float(tst[2].replace("\n","")))
                        else:
                            Y.append(float(tst[1].replace("\n","")))
                    else:
                        if i == 0:
                            pass
                        else:
                            MxAng1.append(tst[1].strip('][').split(', '))
                           # MxAng2.append(tst[8].strip('][').split(', '))
                            V.append(tst[2].strip('][').split(', '))
                            T.append(tst[3].strip('][').split(', '))
                global lenX
                lenX = len(X)
                bx.plot(X, Y, color = 'b')
                if Y2 != []:
                    bx.plot(X, Y2, color = 'r')

                for i,t in enumerate(T):
                    bx.text(float(t[1])+0.5, float(max(Y)) + 7, 'Rep '+str(i+1))
                    bx.text(float(t[1])+0.5, float(max(Y)) + 5, 'Max. Angle '+ str(MxAng1[i][0]))
                  #  bx.text(float(t[1])+0.5, float(max(Y)) + 3, 'Max. Angle '+ str(MxAng2[i][0]))
                    bx.text(float(t[1])+0.5, float(max(Y)) + 1, 'Max. Vel. '+max(V[i]))
                    bx.axvline(x = float(t[1]), color = 'b', linestyle = "dashed")
                    bx.axvline(x = float(t[-1]) + 2, color = 'b', linestyle = "dashed")
                update(1)
            
            except:
                label.config( text = "No Correct Data" )
        def update(val):
            
            pos = s_time.val
            bx.axis([pos, pos+10, 0, 30])
            fig.canvas.draw_idle()
        # Dropdown menu options
        options = dir_list
          
        # datatype of menu text
        clicked = StringVar()
          
        # initial menu text
        clicked.set( "Select File to View" )
          
        # Create Dropdown menu
        drop = OptionMenu(tab3 , clicked , *options )
        drop.grid(row=0,columnspan=5)
          
        # Create button, it will change label text
        button = Button(tab3 , text = "View" , command = show ).grid(row=1,columnspan=5)
          
        # Create Label
        label = Label(tab3 , text = " " )
        label.grid(row=2,columnspan=5)

        fig = plt.Figure(figsize=(8,3))
        canvas = FigureCanvasTkAgg(fig, tab3)
        canvas.get_tk_widget().grid(row=3,columnspan=5)
        
        global bx
        bx=fig.add_subplot(111)
        fig.subplots_adjust(bottom=0.25)

        bx.axis([0, 9, 0, 30])
        bx_time = fig.add_axes([0.12, 0.1, 0.78, 0.03])
        s_time = Slider(bx_time, 'Time', 0, 1000, valinit=0)
        s_time.on_changed(update)
        
         ################################################TAB 4 STUFF############################################################################
        #Label(tab4,text="App Activity Dashboard", font = 'Helvetica 20').grid(row=0,columnspan=3)
        figtab4 = plt.Figure(figsize=(5,2))
        canvas = FigureCanvasTkAgg(figtab4, tab4)
        canvas.get_tk_widget().grid(row=1,column=0, pady = 10)
        
        figtab4x=figtab4.add_subplot(111)
        figtab4x.set_ylabel('Repetitions')
        figtab4x.set_title('Repetitions per Day')
        figtab4x.plot(df["Day"], DfVal1)
        figtab4x.tick_params(axis='x', labelrotation = 90)
        
        fig2tab4 = plt.Figure(figsize=(5,2))
        canvas = FigureCanvasTkAgg(fig2tab4, tab4)
        canvas.get_tk_widget().grid(row=1,column=1, pady = 10)
        
        fig2tab4x=fig2tab4.add_subplot(111)
        fig2tab4x.set_ylabel('Usage Time')
        fig2tab4x.set_title('Session Length')
        fig2tab4x.bar(df["Day"], DfVal2)
        fig2tab4x.tick_params(axis='x', labelrotation = 90)
        
        fig3tab4 = plt.Figure(figsize=(5,2))
        canvas = FigureCanvasTkAgg(fig3tab4, tab4)
        canvas.get_tk_widget().grid(row=2,column=1)
        
        fig3tab4x=fig3tab4.add_subplot(111)
        fig3tab4x.set_ylabel('Resting Time')
        fig3tab4x.set_title('Resting Time Per Session')
        fig3tab4x.bar(df["Day"], DfVal3)
        fig3tab4x.tick_params(axis='x', labelrotation = 90)
        
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
        
        ButtonPin = 14
        lastTnumber = int(MaxStretch)
        global MaxAngle
        if lastTnumber != 0:
            Default = 0
            if lastTnumber == 1 or lastTnumber == 2:
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
            
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(ButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(ButtonPin2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(ButtonPin3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        i2c = I2C(1)  # Device is /dev/i2c-1
        sensor = adafruit_bno055.BNO055_I2C(i2c, address= 0x28)
        sensor2 = adafruit_bno055.BNO055_I2C(i2c, address= 0x29)
        plt.style.use('fivethirtyeight')

        def Ibutton(channel):
            qw2 = sensor2.quaternion[0]
            Rad2Deg = 180/pi
            
            if qw2 is None:
                pass
            else:
                try:
                    btn1[11] = round(2*acos(qw2)*Rad2Deg, 2)
                except: 
                    pass
            
            if btn2[0] != 0 and btn1[1] == False:
                btn2[0] = 0
                btn2[3] = "Keep on good job!"
                    
            elif btn2[0] == 0 and btn1[1] == True and time.time()-btn1[7]>2 and btn2[2] == False: # and btn2[7] == False
                btn2[8] += 1
                if btn2[8] == 3:
                    btn2[2] = True
                    btn2[3] = "Stretch Failure"
                btn2[3] = "Didn't Reach Target, Try Going Higher"
                
            if btn1[0] == 0 and time.time()-btn1[7]>0.5:
                if btn2[2] == True and not btn2[4] == 3: #<-----------------------CHANGED HERE, CHECK PERFORMANCE AFTER SET 3
                    btn2[3] = "Wait Until Timer is Over"
                else:
                    if btn2[2] == False:
                        btn1[0] = 1
                        btn1[1] = True
                        btn1[7] = time.time()
                
            elif btn1[0] == 1 and time.time()-btn1[7]>0.5:
                btn1[6] += 1
                info.append([btn1[6],btn1[5],btn1[2],btn1[8],btn1[10],btn2[11]])
                print('Repetition\tMax Angle\tAvg. Velocity(cm/s)\tTime\tDistance\n'+str(btn1[6])+'\t'+str(btn1[5])+'\t'*2+str(btn1[2])+'\t'+str(btn1[8])+'\t'+str(btn1[10])+'\n')
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
                
        GPIO.add_event_detect(ButtonPin, GPIO.RISING,callback=Ibutton)

        def Fbutton2(channel):
            if btn1[1] == True and btn2[1] == False and btn2[2] == False:
                btn2[8] = 0
                btn2[0] = 1
                btn2[3] = "Good Stretch!"
                btn2[1] = True
                btn2[6] = 0
                btn2[7] = False
            
        GPIO.add_event_detect(ButtonPin2, GPIO.RISING,callback=Fbutton2)

        class MainWindow(Tk):
            def __init__(self):
                Tk.__init__(self)
                self.geometry('1200x900')
                myFont = font.Font(family='Helvetica', size=40, weight='bold')

                # the figure that will contain the plot
                self.fig = Figure(figsize = (11, 6), dpi = 50)
                self.plot1 = self.fig.add_subplot(111)
                self.canvas = FigureCanvasTkAgg(self.fig, master = self)
                self.canvas.draw()
                self.canvas.get_tk_widget().grid(row=2,column=0)
                
                global sets_and_rep, Messages
                sets_and_rep = StringVar(self)
                Messages = StringVar(self)
                sets_and_rep.set("Set: %d Rep: %d TA: %.1f" % (btn2[4], btn1[6], MaxAngle))
                Messages.set(str(btn2[3]))
                self.Rep = Label(self, textvariable = sets_and_rep, font = 'Helvetica 20')
                self.Mes = Label(self, textvariable = Messages, bg='SpringGreen3', fg='black', font = 'Helvetica 20', height = 2, width=60)
                self.Mes.grid(row=0,columnspan=3)
                self.Rep.grid(row=1,columnspan=3, sticky = "W") #user[0][0]<---Used to get user info
                
                s = ttk.Style()
                s.theme_use('clam')
                s.configure("red.Vertical.TProgressbar", background='red')
                s.configure("yellow.Vertical.TProgressbar", background='yellow')
                s.configure("green.Vertical.TProgressbar", background='green')
                
                self.PB = ttk.Progressbar(self, orient='vertical', mode='determinate', length=300, maximum = 30, style='red.Vertical.TProgressbar')
                self.PB.grid(row=2,column=1, sticky = "W")
                self.Stop = Button(self, text="Stop", bg='firebrick1', fg='white', font='Helvetica 20', height = 10, width=15, command=self.close).grid(row=2,column=2, sticky = "W")
                self.ani = FuncAnimation(self.fig, self.plot, interval = 20)
            
            def close(self):
                Box = messagebox.askquestion('Message', "Save Today's Performance?")
                if Box == 'yes':
                    current_time = datetime.datetime.now()
                    current_day = datetime.date.today()
                    today = str(current_day) + '_' +str(current_time.hour) + '_' + str(current_time.minute)
                    
                    with open("Users/"+user[0][3]+"/"+today+".txt", "a") as f:
                        f.write("Repetition\tMax. Angle Reached1\tAvg. Velocity\tTime\tDistance\tDefault="+str(Default)+"\tMax Target Angle="+str(MaxAngle)+"\tMax. Angle Reached2"+"\n")
                        for l in info:
                            f.write(str(l[0])+"\t"+str(l[1])+"\t"+str(l[2])+"\t"+str(l[3])+"\t"+str(l[4])+"\t"+str(l[5])+"\n")
                        f.write("X(Time)\tY(Sensor 1 Angle)\tY(Sensor 2 Angle)\n")
                        for xs,ys,y2s in zip(x,y,y2):
                            f.write(str(xs)+'\t' + str(ys) +'\t' + str(y2s) +'\n')
                            
                    with open("Users/"+user[0][3]+"/info.txt", "a") as file:
                            file.write("Day"+str(day)+'\t'+str(btn1[6])+'\t'+str(max(x))+'\t'+str(y.count(0))+'\n')
                          
                    root.destroy()
                   # pop.destroy()
                    
                elif Box == 'no':
                    root.destroy()
                    #pop.destroy()
                else:
                    root.destroy()
                   # pop.destroy()
                
               # p1.terminate()
                #p2.terminate()
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
                GPIO.cleanup()
                
            def plot(self,i):
               # self.PB['value'] = y[-1]
               # if self.PB['value'] >= 10 and self.PB['value'] < 15:
               #     self.PB.config(style='yellow.Vertical.TProgressbar')
               # elif self.PB['value'] >= 15:
               #     self.PB.config(style='green.Vertical.TProgressbar')
               # else:
               #     self.PB.config(style='red.Vertical.TProgressbar')
                try:                        
                    sets_and_rep.set("Set: %d Rep: %d TA: %.1f" % (btn2[4], btn1[6], MaxAngle))
                    Messages.set(str(btn2[3]))
                    self.plot1.set(xlim =(x[-1]-15, x[-1]+5), ylim =(-1, 40))
                    self.plot1.set_xlabel('Time (s)')
                    self.plot1.set_ylabel('Angle (Degress)')
                    self.plot1.plot(x,y, color='blue')
                    self.plot1.plot(x,y2, color='red')
                   # self.plot1.legend([str(round(btn2[10], 2)) + 'deg/s'], prop={'size':40}, handletextpad=0, handlelength =0)
                    self.plot1.legend([str(round(y[-1], 2)) + 'deg' + '\n' + str(round(y2[-1], 2)) + 'deg'], prop={'size':40}, handletextpad=0, handlelength =0)
                    self.canvas.draw()
                    
                except:
                    pass #self.plot(1)

        def loop():
            root.mainloop()
            
        def Calculations():
            while True:
                if btn2[2] == False:
                    qw = sensor.quaternion[0]
                    qw2 = sensor2.quaternion[0]
                    r = 126
                    Rad2Deg = 180/pi
                    
                    ########### INITIATING INITIAL ANGLE FOR BOTH SENSORS #############
                    while btn1[9] <= 0 or btn1[9] >100:
                        qw = sensor.quaternion[0]
                        if qw is None:
                            continue
                        else:
                            try:
                                btn1[9] = round(2*acos(qw)*Rad2Deg, 2)
                            except:
                                pass
                            
                    while btn1[11] <= 0 or btn1[11] >100:
                        qw2 = sensor2.quaternion[0]
                        if qw2 is None:
                            continue
                        else:
                            try:
                                btn1[11] = round(2*acos(qw2)*Rad2Deg, 2)
                            except: 
                                pass
                    ########################## STARTING ANGLE CALCULATIONS ####################
                    
                    if btn1[0] == 0:
                        a = 0
                        a2 = 0
                        if qw is None:
                            qw = qw1[-1]
                        else:
                            try:
                                testAngle = round(2*acos(qw)*Rad2Deg, 2) # I used this to test if an angle can be calulated and proper qw values are stored
                            except: 
                                qw = qw1[-1]
                                
                        if qw2 is None:
                            qw2 = qw2_1[-1]
                        else:
                            try:
                                testAngle = round(2*acos(qw2)*Rad2Deg, 2) # I used this to test if an angle can be calulated and proper qw values are stored
                            except: 
                                qw2 = qw2_1[-1]
                                
                    else:
                        if qw is None:
                            qw = qw1[-1]
                            a = round(2*acos(qw)*Rad2Deg, 2) - btn1[9]
                        else:
                            try:
                                a = round(2*acos(qw)*Rad2Deg, 2) - btn1[9]
                            except: 
                                qw = qw1[-1]
                                a = round(2*acos(qw)*Rad2Deg, 2) - btn1[9]
                                
                        if qw2 is None:
                            qw2 = qw2_1[-1]
                            a2 = round(2*acos(qw2)*Rad2Deg, 2) -btn1[11]
                        else:
                            try:
                                a2 = round(2*acos(qw2)*Rad2Deg, 2) - btn1[11]
                            except: 
                                qw2 = qw2_1[-1]
                                a2 = round(2*acos(qw2)*Rad2Deg, 2) - btn1[11]
                                
                    qw1.append(qw)
                    qw2_1.append(qw2)
                    y.append(round(a, 2))
                    y2.append(round(a2, 2))
                    x.append(next(index))  

                    if btn1[1] == True:
                        if btn1[2][-1] == 0:
                            btn1[3] = x[-1] #init. time
                            btn1[4] = x[-1] + 1 # final time
                        else:
                            btn1[4] = x[-1]
                            
                        if y[-1] > btn1[5]:
                            btn1[5] = y[-1] # Setting max angle
                            
                        if y2[-1] > btn2[11]:
                            btn2[11] = y2[-1] # Setting max angle
                            
                        Time = btn1[4]-btn1[3]
                        if Time == 0:
                            v = 0
                        else:
                            #v = abs(btn2[10] - (y[-1]/Time))
                            v = y[-1]/Time
                            
                        btn2[10] = v
                        
                        btn1[10].append(round(2*pi*r*(a/360), 2))
                        btn1[2].append(round(v,2))
                        btn1[8].append(x[-1])
                        
                        if v <= 0.5 and btn2[0] == 0:
                            if btn2[7] == False:
                                btn2[6] = time.time()
                                btn2[7] = True
                            else:
                                if time.time()-btn2[6]>4:
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
                    
                    if time.time()-btn1[7]>1.5 and btn2[5] == False: #Used to display messages
                        if btn2[4] == 3:
                            btn2[3] = "Routine Has Ended. Click On Stop"
                        else:
                            btn2[5] = True
                            btn1[7] = time.time()
                            btn2[9] = btn1[6] - btn2[9]
                            btn2[3] = "Return To Home And Rest For " + str(round((btn2[9]*20)/60,2)) + " minutes"
                    elif time.time()-btn1[7]>btn2[9]*20 and btn2[5] == True:#This will reset the system to continue
                        btn2[4] += 1
                        btn2[2] = False
                        btn2[5] = False
                        btn1[7] = time.time()
                        btn2[8] = 0
                        btn2[3] = "Continue"
                        
                    elif time.time()-btn1[7]>2 and btn2[5] == True:
                        time2Display = btn2[9]*20 - (time.time()-btn1[7]) # change value multiplying btn2[9] to change resting time 20 = 0.2 sec per repetition
                        if time2Display/60 < 1:
                            minute = 0
                            seconds = int(time2Display%60)
                        else:
                            minute = int((time2Display - time2Display%60)/60)
                            seconds = int(time2Display%60)
                        btn2[3] = str(minute) + ":" + str(seconds) + " remaining"
                    
                    time.sleep(1)
                    
        if __name__ == '__main__':
            with Manager() as manager:
                index = count()
                x = manager.list([])
                y = manager.list([])
                
                y2 = manager.list([])
                
                qw1 = manager.list([0])
                qw2_1 = manager.list([0])
                ####################[clicked, false/ true when clicked, velocity values, init. time, final time, max angle, repetition, time when clicked, init. rot angle, angle Values, , init. rot angle 2]
                btn1 = manager.list([0, False, manager.list([0]), 0, 0, 0, 0, time.time(), manager.list([0]), 0, manager.list([0]), 0])
                ####################[clicked and # cycles to display "keep on good job", Used to detect when reached goal, stop workout, value for messages, # set, check point to display message, set timer when velocity = 0, check point for vel timer, bit used to know if streatch failure has reached 3 times, # repetitions per set, avg. vel]
                btn2 = manager.list([0, False, False, "", 1, False, 0, False, 0, 0, 0, 0])
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

