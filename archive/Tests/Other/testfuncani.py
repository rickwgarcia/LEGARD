from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import * 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


fig = plt.Figure()
x = np.arange(0, 2*np.pi, 0.01)

def animate(i):
    for j in range(10000000):
        k=j
    line.set_ydata(np.sin(x + i / 10.0))
    return line

root = Tk()

label = Label(root, text="Graph")
label.grid(column=0, row=0)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(column=0, row=1)

ax = fig.add_subplot(111)
line, = ax.plot(x, np.sin(x))

ani = FuncAnimation(fig, animate, interval=20)

mainloop()