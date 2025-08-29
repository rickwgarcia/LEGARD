from itertools import count
from tkinter import * 
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from multiprocessing import Process, Manager
import tkinter.font as font
from tkinter import Tk, Button, Label
from sys import argv
from tkinter import messagebox
import time
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055
from math import *
import RPi.GPIO as GPIO
import datetime

t = []
for a in argv:
    if a == argv[0]:
        pass
    else:
        t.append(str(a))
print(t)

ButtonPin = 16
ButtonPin2 = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(ButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ButtonPin2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

i2c = I2C(1)  # Device is /dev/i2c-1
sensor = adafruit_bno055.BNO055_I2C(i2c)
plt.style.use('fivethirtyeight')

def button(channel):
    if btn2[0] != 0 and btn1[1] == True:
        print('Keep on good job!')
        btn2[0] -= 1
        btn2[3] = 1
            
    elif btn2[0] == 0 and btn1[1] == True:
        print('Try higher next stretch')
        btn2[3] = 2
        
    if btn1[0] == 0:
        btn1[0] = 1
        btn1[1] = True
    else:
        btn1[6] += 1
        info.append([btn1[6],btn1[5],btn1[2]])
        print('Cycle\t'+'Max Legth(cm)\t'+'Avg. Velocity(cm/s)\n'+str(btn1[6])+'\t'+str(btn1[5])+'\t'*2+str(btn1[2])+'\n')
        btn1[0] = 0
        btn1[1] = False
        btn1[2] = 0
        btn1[3] = 0
        btn1[4] = 0
        btn1[5] = 0
        
GPIO.add_event_detect(ButtonPin, GPIO.RISING,callback=button)

def button2(channel):
    if btn1[1] == True:
        print('Good Stretch!\n')
        btn2[0] = 3
        btn2[2] += 1
        btn2[3] = 3
    
GPIO.add_event_detect(ButtonPin2, GPIO.RISING,callback=button2)

class MainWindow(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.geometry('1200x900')
        myFont = font.Font(family='Helvetica', size=25, weight='bold')

        # the figure that will contain the plot
        self.fig = Figure(figsize = (12, 6), dpi = 100)
        self.plot1 = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master = self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=2,columnspan=3)
        
        self.User = Label(self, text = "User: "+t[0], font = 'Helvetica 20').grid(row=1,column=2)
        
        ##################### MESSAGES TO DISPLAY ####################
        self.Mes1 = Label(self, text = " ", bg='SpringGreen3', fg='black', font = 'Helvetica 20', height = 2, width=60)
        self.Mes2 = Label(self, text = "Keep on good job!", bg='SpringGreen3', fg='black', font = 'Helvetica 20', height = 2, width=60)
        self.Mes3 = Label(self, text = "Try higher next stretch", bg='SpringGreen3', fg='black', font = 'Helvetica 20', height = 2, width=60)
        self.Mes4 = Label(self, text = "Good Stretch!", bg='SpringGreen3', fg='black', font = 'Helvetica 20', height = 2, width=60)
        self.Mes1.grid(row=0,columnspan=3)
        
        self.Stop = Button(self, text="Stop", bg='firebrick1', fg='white', font=myFont, height = 5, width=10, command=self.close).grid(row=3,column=1)
        self.ani = FuncAnimation(self.fig, self.plot, interval = 20)
    
    def close(self):
        #p1.terminate()
        Box = messagebox.askquestion('Message', 'Save Data?')
        if Box == 'yes':
            current_time = datetime.datetime.now()
            current_day = datetime.date.today()
            today = str(current_day) + ' ' +str(current_time.hour) + ':' + str(current_time.minute)
            
            with open("Users/"+t[1]+"/"+today+".txt", "a") as f:
                for xs,ys in zip(x,y):
                    f.write(str(xs)+'\t' + str(ys)+'\n')
                    
            with open("Users/"+t[1]+"/info.txt", "a") as file:
                    file.write(Day+str(t[2])+'/t'+btn1[6])
                    
            root.destroy()
            
        elif Box == 'no':
            root.destroy()
        else:
            root.destroy()
        
    def plot(self,i):
        try:
            if btn2[3] != 0:
                self.PackLabel()
            self.plot1.set(xlim =(x[-1]-15, x[-1]+5), ylim =(-1, 80))
            self.plot1.set_xlabel('Time (s)')
            self.plot1.set_ylabel('Distance (cm)')
            self.plot1.plot(x,y, color='green')
            self.canvas.draw()
            
        except:
            self.plot(1)
            
    def PackLabel(self):
        if btn2[3] == 1:
            self.Mes1.grid_forget()
            self.Mes3.grid_forget()
            self.Mes4.grid_forget()
            self.Mes2.grid(row=0,columnspan=3)
        elif btn2[3] == 2:
            self.Mes1.grid_forget()
            self.Mes2.grid_forget()
            self.Mes4.grid_forget()
            self.Mes3.grid(row=0,columnspan=3)
        elif btn2[3] == 3:
            self.Mes1.grid_forget()
            self.Mes2.grid_forget()
            self.Mes3.grid_forget()
            self.Mes4.grid(row=0,columnspan=3)
        return

def loop():
    root.mainloop()
    
def Calculations():
    while True:
        qw = sensor.quaternion[0]
        r = 80
        try:
            a = round(2*acos(qw)*57.2957795131, 2)
            qw1.append(qw)
            if btn1[0] == 0:
                a=0
            y.append(round(2*pi*r*(a/360), 2))
            x.append(next(index))
            time.sleep(1)
        except:
            try:
                qw = qw1[-2]
            except:
                qw = qw1[-1]
            a = round(2*acos(qw)*57.2957795131, 2)
            qw1.append(qw)
            if btn1[0] == 0:
                a=0
            y.append(round(2*pi*r*(a/360), 2))
            x.append(next(index))
            time.sleep(1)
        if btn1[1] == True:
            if btn1[2] == 0:
                btn1[3] = x[-1] #init. time
                btn1[4] = x[-1] + 1 # final time
            else:
                btn1[4] = x[-1]
                
            v = y[-1]/(btn1[4]-btn1[3])
            if v > btn1[2]:
                btn1[2] = v
            if y[-1] > btn1[5]:
                btn1[5] = y[-1]
                
if __name__ == '__main__':
    with Manager() as manager:
        index = count()
        x = manager.list([])
        y = manager.list([])
        qw1 = manager.list([])
        ####################[clicked, false/ true when clicked, max velocity, init. time, final time, max distance, cycle, time when clicked]
        btn1 = manager.list([0, False, 0, 0, 0, 0, 0, 0])
        ####################[clicked and # cycles to display "keep on good job", false, # reached, bit for messages, time when clicked]
        btn2 = manager.list([0, False, 0, 0, 0])
        info = manager.list([])
        
        root = MainWindow()
        p1 = Process(target = Calculations)
        p2 = Process(target = loop)
        p1.start()
        p2.start()
        p1.join()
        p2.join()
sys.exit(0)
