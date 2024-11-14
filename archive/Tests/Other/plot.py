from itertools import count
from tkinter import * 
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from multiprocessing import Process, Manager
import tkinter.font as font
from tkinter import Tk, Button, Label, ttk
from sys import argv
from tkinter import messagebox
import time
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055
from math import *
import RPi.GPIO as GPIO
import datetime

t = 8
ButtonPin = 14
lastTnumber = int(t)
if lastTnumber != 0:
    if lastTnumber == 1 or lastTnumber == 2:
       ButtonPin2 = 15
    elif lastTnumber == 3:
       ButtonPin2 = 18
    elif lastTnumber == 4:
       ButtonPin2 = 23
    elif lastTnumber == 5:
       ButtonPin2 = 24
    elif lastTnumber == 6:
       ButtonPin2 = 25
    elif lastTnumber == 7:
       ButtonPin2 = 8
    elif lastTnumber == 8:
       ButtonPin2 = 7
    elif lastTnumber == 9:
       ButtonPin2 = 1
    elif lastTnumber == 10:
       ButtonPin2 = 12
else:
    ButtonPin2 = 12
    
GPIO.setmode(GPIO.BCM)
GPIO.setup(ButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(ButtonPin2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

i2c = I2C(1)  # Device is /dev/i2c-1
sensor = adafruit_bno055.BNO055_I2C(i2c)
plt.style.use('fivethirtyeight')

def button(channel):
    if btn2[0] != 0 and btn1[1] == False:
        print('Keep on good job!')
        btn2[0] -= 1
        btn2[3] = 1
            
    elif btn2[0] == 0 and btn1[1] == True and time.time()-btn1[7]>2:
        print('Try higher next stretch')
        btn2[3] = 2
        
    if btn1[0] == 0 and time.time()-btn1[7]>0.5:
        btn1[0] = 1
        btn1[1] = True
        btn1[7] = time.time()
        
    elif btn1[0] == 1 and time.time()-btn1[7]>2:
        btn1[6] += 1
        info.append([btn1[6],btn1[5],btn1[2]])
        print('Cycle\tMax Legth(cm)\tAvg. Acceleration(cm/s^2)\tTime\n'+str(btn1[6])+'\t'+str(btn1[5])+'\t'*2+str(btn1[2])+'\t'+str(btn1[8])+'\n')
        btn1[0] = 0
        btn1[1] = False
        btn1[2] = manager.list([0])
        btn1[3] = 0
        btn1[4] = 0
        btn1[5] = 0
        btn2[1] = False
        btn1[7] = time.time()
        btn1[8] = manager.list([0])
        btn1[9] = manager.list([0])
        
GPIO.add_event_detect(ButtonPin, GPIO.RISING,callback=button)

def button2(channel):
    if btn1[1] == True and btn2[1] == False:
        btn2[0] = 3
        btn2[2] += 1
        btn2[3] = 3
        btn2[1] = True
    
GPIO.add_event_detect(ButtonPin2, GPIO.RISING,callback=button2)

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
        self.canvas.get_tk_widget().grid(row=1,column=0)
        
        ##################### MESSAGES TO DISPLAY ####################
        self.Mes1 = Label(self, text = " ", bg='SpringGreen3', fg='black', font = 'Helvetica 20', height = 2, width=60)
        self.Mes2 = Label(self, text = "Keep on good job!", bg='SpringGreen3', fg='black', font = 'Helvetica 20', height = 2, width=60)
        self.Mes3 = Label(self, text = "Try higher next stretch", bg='SpringGreen3', fg='black', font = 'Helvetica 20', height = 2, width=60)
        self.Mes4 = Label(self, text = "Good Stretch!", bg='SpringGreen3', fg='black', font = 'Helvetica 20', height = 2, width=60)
        self.Mes1.grid(row=0,columnspan=3)
        
        s = ttk.Style()
        s.theme_use('clam')
        s.configure("red.Vertical.TProgressbar", background='red')
        s.configure("yellow.Vertical.TProgressbar", background='yellow')
        s.configure("green.Vertical.TProgressbar", background='green')
        
        self.PB = ttk.Progressbar(self, orient='vertical', mode='determinate', length=300, maximum = 30, style='red.Vertical.TProgressbar')
        self.PB.grid(row=1,column=1)
        self.Stop = Button(self, text="Stop", bg='firebrick1', fg='white', font=myFont, height = 5, width=10, command=self.close).grid(row=1,column=2, sticky = "W")
        self.ani = FuncAnimation(self.fig, self.plot, interval = 20)
        
    def close(self):
        #p1.terminate()
        Box = messagebox.askquestion('Message', "Save Today's Performance?")
        if Box == 'yes':
            current_time = datetime.datetime.now()
            current_day = datetime.date.today()
            today = str(current_day) + ' ' +str(current_time.hour) + ':' + str(current_time.minute)
            root.destroy()
            
        elif Box == 'no':
            root.destroy()
        else:
            root.destroy()
        
    def plot(self,i):
        self.PB['value'] = y[-1]
        if self.PB['value'] >= 10 and self.PB['value'] < 15:
            self.PB.config(style='yellow.Vertical.TProgressbar')
        elif self.PB['value'] >= 15:
            self.PB.config(style='green.Vertical.TProgressbar')
        else:
            self.PB.config(style='red.Vertical.TProgressbar')
        try:
            
            if btn2[3] != 0:
                self.PackLabel()
            self.plot1.set(xlim =(x[-1]-15, x[-1]+5), ylim =(-1, 40))
            self.plot1.set_xlabel('Time (s)')
            self.plot1.set_ylabel('Angle (degrees)')
            self.plot1.plot(x,y, color='blue')
            self.plot1.legend([str(round(btn1[2][-1], 2)) + 'cm/s^2'], prop={'size':40}, handletextpad=0, handlelength =0)##<<<<<<<------------------HERE
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
        qw = sensor.quaternion[1]
        r = 126
        while init.value <= 0.0 or init.value >100.0:
            qw = sensor.quaternion[1]
            if qw is None:
                continue
            else:
                init.value = round(2*asin(qw)*57.2957795131, 2)        
        try:
            if btn1[0] == 0:
                a=0
            else:
                a = round(2*asin(qw)*57.2957795131, 2) - init.value
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
                    a = round(2*asin(qw)*57.2957795131, 2) - init.value
                    qw1.append(qw1[-1])
                except:
                    a = round(2*asin(qw1[-2])*57.2957795131, 2) - init.value
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
            v = (y[-1] - y[-2]) / (btn1[4]-btn1[3])
            btn1[10].append(round(2*pi*r*(a/360), 2))
            btn1[2].append(round(v,2))
            btn1[8].append(x[-1])
if __name__ == '__main__':
    with Manager() as manager:
        index = count()
        x = manager.list([])
        y = manager.list([])
        qw1 = manager.list([0])
        init = Manager().Value('i',0)
        ####################[clicked, false/ true when clicked, max velocity, init. time, final time, max distance, cycle, time when clicked, velocity values]
        btn1 = manager.list([0, False, manager.list([0]), 0, 0, 0, 0, time.time(), manager.list([0]),0,manager.list([0])])
        ####################[clicked and # cycles to display "keep on good job", false, # reached, bit for messages]
        btn2 = manager.list([0, False, 0, 0])
        info = manager.list([])
        
        root = MainWindow()
        p1 = Process(target = Calculations)
        p2 = Process(target = loop)
        p1.start()
        p2.start()
        p1.join()
        p2.join()