from bluetooth import *
from itertools import count
from tkinter import * 
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from multiprocessing import Process, Manager
import tkinter.font as font
from tkinter import Tk, Button, Label
class MainWindow(Tk):
    def __init__(self):
        Tk.__init__(self)

        self.geometry('1500x1000')
        myFont = font.Font(family='Helvetica', size=15, weight='bold')
        #MAC address of ESP32
        addr = "78:21:84:88:A9:BE"
        service_matches = find_service( address = addr )

        buf_size = 1024;

        if len(service_matches) == 0:
            self.NoConn= Label(self, text = "Couldn't find the Tool. Go back, turn on device and start again.", font = 'Helvetica 20').grid(row=0,column=0)#.pack(side = TOP, anchor=NW)#place(x=200, y=800)
            #sys.exit(0)

        # the figure that will contain the plot
        self.fig = Figure(figsize = (14, 8), dpi = 100)
        self.plot1 = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master = self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1,column=0)#.pack()
        #self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        #self.toolbar.update()
        
        self.Name = Label(self, text = "Name: ", font = 'Helvetica 30').grid(row=0,column=0)#.pack(side = TOP, anchor=NW)
        self.Start = Button(self, text="Start/Stop", bg='SpringGreen3', fg='white', height= 3, width=10, font=myFont).grid(row=2,column=0, sticky='w')#.pack(side = TOP, anchor=NW)
        self.Back = Button(self, text="Back", bg='gold', fg='black', font=myFont, width=10, command=self.close).grid(row=3,column=0, sticky='w')#.pack(side = TOP, anchor=NW)
        self.ani = FuncAnimation(self.fig, self.plot, interval = 20)
    
    def close(self):
        root.destroy()
        sock.close()
        p1.terminate()
        #p2.terminate()
        
    def plot(self,i):
        try:
            self.plot1 = self.fig.add_subplot(111)
            self.plot1.plot(x,y, color='green')
            self.canvas.draw()
            
        except:
            self.plot(1)

def loop():
    root.mainloop()
    
def rx_and_echo():
    while True:
        data = sock.recv(buf_size)
        if data:
            x.append(next(index))
            y.append(int(data.decode('utf-8')))
        print(x[-1])

if __name__ == '__main__':
    with Manager() as manager:
        addr = "78:21:84:88:A9:BE"
        service_matches = find_service( address = addr )

        buf_size = 1024;
        if len(service_matches) == 0:
            pass
        else:
            first_match = service_matches[0]
            port = first_match["port"]
            name = first_match["name"]
            host = first_match["host"]

            port=1
            # Create the client socket
            sock=BluetoothSocket(RFCOMM)
            sock.connect((host, port))
        index = count()
        x = manager.list([])
        y = manager.list([])
        
        root = MainWindow()
        p1 = Process(target = rx_and_echo)
        p2 = Process(target = loop)
        p1.start()
        p2.start()
        p1.join()
        p2.join()
sys.exit(0)