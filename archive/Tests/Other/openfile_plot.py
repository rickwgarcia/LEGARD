from tkinter import * 
from tkinter.filedialog import askopenfile
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

x = []
y = []
def plot():

    # the figure that will contain the plot
    fig = Figure(figsize = (14, 8), dpi = 100)

    # adding the subplot
    plot1 = fig.add_subplot(111)

    # plotting the graph
    plot1.plot(x,y)

    # creating the Tkinter canvas
    # containing the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig, master = root)
    canvas.draw()

    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().pack()

    # creating the Matplotlib toolbar
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()

    # placing the toolbar on the Tkinter window
    canvas.get_tk_widget().pack()

root = Tk()
root.geometry('1500x800')

def open_file():
    file = askopenfile(mode ='r', filetypes =[('Text Files', '*.txt')])
    if file is not None:
        content = file.read().split()
        for i,c in enumerate(content):
            if (i%2) == 0:
                x.append(c)
            else:
                y.append(c)
        f = str(file).split()
        f = f[1].split('/')
        print(f[6])
        #plot()
        
btn = Button(root, text ='Open', command = open_file)
btn.pack(side = TOP, pady = 10)
  
mainloop()