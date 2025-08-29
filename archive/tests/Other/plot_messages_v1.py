from itertools import count
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from multiprocessing import Process, Manager
import time
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055
from math import *
import RPi.GPIO as GPIO

ButtonPin = 16
ButtonPin2 = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(ButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ButtonPin2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# To enable i2c-gpio, add the line `dtoverlay=i2c-gpio` to /boot/config.txt
# Then reboot the pi
# Create library object using our Extended Bus I2C port
# Use `ls /dev/i2c*` to find out what i2c devices are connected
i2c = I2C(1)  # Device is /dev/i2c-1
sensor = adafruit_bno055.BNO055_I2C(i2c)
plt.style.use('fivethirtyeight')

def button(channel):
    if btn2[0] != 0 and btn1[1] == True:
        print('Keep on good job!')
        btn2[0] -= 1
            
    elif btn2[0] == 0 and btn1[1] == True:
        print('Try higher next stretch')
        
    if btn1[0] == 0:
        btn1[0] = 1
        btn1[1] = True
    else:
        btn1[6] += 1
        info.append([btn1[6],btn1[5],btn1[2]])
        print('Cycle\t'+'Max Legth(cm)\t'+'Max Velocity(cm/s)\n'+str(btn1[6])+'\t'+str(btn1[5])+'\t'*2+str(btn1[2])+'\n')
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
    
GPIO.add_event_detect(ButtonPin2, GPIO.RISING,callback=button2)

def Calculations():
    while True:
        qw = sensor.quaternion[0]
        r = 10
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
                btn1[3] = x[-1] #init. velocity
                btn1[4] = x[-1] + 1 # final velocity
            else:
                btn1[4] = x[-1]
                
            v = y[-1]/(btn1[4]-btn1[3])
            if v > btn1[2]:
                btn1[2] = v
            if y[-1] > btn1[5]:
                btn1[5] = y[-1]
        
def plot(i):
    try:
        plt.cla()
        plt.xlabel('Time (s)')
        plt.ylabel('Distance (cm)')
        plt.plot(x,y)
    except:
        plot(1)
    
def animation():
    ani = FuncAnimation(plt.gcf(), plot)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    with Manager() as manager:
        index = count()
        x = manager.list([])
        y = manager.list([])
        qw1 = manager.list([])
        ####################[clicked, false, max velocity, init. time, final time, max distance, cycle]
        btn1 = manager.list([0, False, 0, 0, 0, 0, 0])
        ####################[clicked and # cycles to display "keep on good job", false, # reached]
        btn2 = manager.list([0, False, 0])
        info = manager.list([])
        
        print('Welcome!!!')
        print("Begin in ")
        for j in [3, 2, 1]:
            print(j)
            time.sleep(1)
        p1 = Process(target = Calculations)
        p2 = Process(target = animation)
        p1.start()
        p2.start()
        p1.join()
        p2.join()
