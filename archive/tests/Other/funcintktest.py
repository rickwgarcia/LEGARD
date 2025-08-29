from bluetooth import *
from itertools import count
from tkinter import * 
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from multiprocessing import Process, Manager
import tkinter.font as font

def plot():
    try:
        plot1 = fig.add_subplot(111)
        
        # plotting the graph
        plot1.plot(x,y)
        plot1.set_xlabel('Time')
        plot1.set_ylabel('Angle')
        #canvas.draw()
        
    except:
        plot()
        
root = Tk()
myFont = font.Font(family='Helvetica', size=15, weight='bold')
root.geometry('1500x1000')

def close():
    p1.terminate()
    root.destroy()
    sock.close()
    #p2.terminate()
        
def rx_and_echo():
    while True:
        data = sock.recv(buf_size)
        if data:
            x.append(next(index))
            y.append(int(data.decode('utf-8')))
        print(x[-1])

def animation():
    ani = FuncAnimation(fig, plot, interval = 20)
    #plt.tight_layout()
    #plt.show()
    
#MAC address of ESP32
addr = "78:21:84:88:A9:BE"
service_matches = find_service( address = addr )

buf_size = 1024;

if len(service_matches) == 0:
    NoConn= Label(root, text = "Couldn't find the Tool. Go back, turn on device and start again.", font = 'Helvetica 20').pack(side = TOP, anchor=NW)#place(x=200, y=800)
    #sys.exit(0)
else:
    first_match = service_matches[0]
    port = first_match["port"]
    name = first_match["name"]
    host = first_match["host"]

    port=1
    # Create the client socket
    sock=BluetoothSocket(RFCOMM)
    sock.connect((host, port))

# the figure that will contain the plot
fig = Figure(figsize = (14, 8), dpi = 100)
plot1 = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master = root)
canvas.get_tk_widget().pack()

Start = Button(root, text="Start/Stop", bg='SpringGreen3', fg='white', height= 3, width=10, font=myFont).pack(side = TOP, anchor=NW)
Back = Button(root, text="Back", bg='gold', fg='black', font=myFont, width=10, command=close).pack(side = TOP, anchor=NW)

if __name__ == "__main__":
    with Manager() as manager:
        index = count()
        x = manager.list([])
        y = manager.list([])
        
        p1 = Process(target = rx_and_echo)
        p2 = Process(target = animation)
        p1.start()
        p2.start()
        p1.join()
        p2.join()
        
