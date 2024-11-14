from tkinter import *
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from tkinter import * 
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
 
# Get the list of all files and directories
path = "/home/si/Desktop/LEGARD/app/Users/admin"
dir_list = os.listdir(path)
# Create object
root = Tk()
  
# Adjust size
root.geometry( "500x500" )
  
# Change the label texta
def show():
    try:
        global ax
        label.config( text = clicked.get() )
        with open(path + "/" + str(clicked.get())) as f:
            line2 = [line.split("\t") for line in f]
        found = False
        X = []
        Y = []
        V = []
        T = []
        ax.cla()
        for i, tst in enumerate(line2):
            if "X(Time)" in tst and found == False:
                found = True
            elif found == True:
                X.append(int(tst[0]))
                Y.append(float(tst[1].replace("\n","")))
            else:
                if i == 0:
                    pass
                else:
                    V.append(tst[2].strip('][').split(', '))
                    T.append(tst[3].strip('][').split(', '))
        
        ax.plot(X,Y)
        
        for i,t in enumerate(T):
            ax.text(float(t[1])+0.5, float(max(Y)) + 2, 'Rep '+str(i+1))
            ax.text(float(t[1])+0.5, float(max(Y)), 'Vel '+max(V[i]))
            ax.axvline(x = float(t[1]), color = 'b', linestyle = "dashed")
            ax.axvline(x = float(t[-1]) + 2, color = 'b', linestyle = "dashed")
        update(1)
    
    except:
        label.config( text = "No Data" )
def update(val):
    pos = s_time.val
    ax.axis([pos, pos+15, 0, 30])
    fig.canvas.draw_idle()

# Dropdown menu options
options = dir_list
  
# datatype of menu text
clicked = StringVar()
  
# initial menu text
clicked.set( "Select File to View" )
  
# Create Dropdown menu
drop = OptionMenu( root , clicked , *options )
drop.pack()
  
# Create button, it will change label text
button = Button( root , text = "View" , command = show ).pack()
  
# Create Label
label = Label( root , text = " " )
label.pack()

fig = plt.Figure()
canvas = FigureCanvasTkAgg(fig, root)
canvas.get_tk_widget().pack()

ax=fig.add_subplot(111)
fig.subplots_adjust(bottom=0.25)

ax.axis([0, 9, 0, 30])
ax_time = fig.add_axes([0.12, 0.1, 0.78, 0.03])
s_time = Slider(ax_time, 'Time', 0, 30, valinit=0)
s_time.on_changed(update)
# Execute tkinter
root.mainloop()