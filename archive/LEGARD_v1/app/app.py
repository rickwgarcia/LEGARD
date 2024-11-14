from tkinter import *
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tkinter import ttk
from PIL import ImageTk, Image
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk) 
import subprocess
import RPi.GPIO as GPIO

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
        GPIO.setup(ButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(ButtonPin2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(ButtonPin3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(ButtonPin4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(ButtonPin5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(ButtonPin6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(ButtonPin7, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(ButtonPin8, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(ButtonPin9, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(ButtonPin10, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
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
            subprocess.run(['python3', 'plot.py', str(user[0][0]), str(user[0][2]), str(len(df)), str(MaxStretch)])
            
        Button(tab2, text="Start Plot", bg='SpringGreen3', fg='white', font = 'Helvetica 20', width = 10, height = 5, command = Start).grid(rowspan=5,column=0)
        
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
                    file.write(username+'\t' + password)
                os.mkdir("Users/"+username) 
                with open("Users/"+username+"/info.txt", "a") as file:
                    file.write(first+'\t'+last+'\t' +gender+'\t' +username+'\t' + password)
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

pop = Tk()
app = Frames()
app.popup(pop)
pop.mainloop()

