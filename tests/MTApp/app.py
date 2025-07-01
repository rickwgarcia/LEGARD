from tkinter import *
from PIL import ImageTk, Image
import tkinter.font as font
from bluetooth import *
from itertools import count
from tkinter import messagebox
from tkinter.filedialog import askopenfile
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk) 
import os

class Frames(object):
                
    def MainScreen(self,root):

        myFont = font.Font(family='Helvetica', size=20, weight='bold')
        width= root.winfo_screenwidth()
        height= root.winfo_screenheight()
        root.geometry("%dx%d" % (width, height))
        root.title('Main Screen')
        
        self.tkpic = ImageTk.PhotoImage(Image.open("unm.png").resize((400, 250)))
        img1 = Label(root, image=self.tkpic).pack(anchor=NW)
        #.grid(row=0, column = 0)
        #.place(x=0, y=0, relwidth=1, relheight=1) #Centered
        
        
        RecordButton = Button(root, text="Record Data", bg='firebrick1', fg='white', font=myFont, command = self.Start).place(x=512, y=450, width=250, height=150, anchor="center")
        AccessButton = Button(root, text="Access Data", bg='SpringGreen3', fg='white', font=myFont, command = self.popup).place(x=1000, y=450, width=250, height=150, anchor="center")

    def Start(self):
        rt = Toplevel(root)
        self.query = StringVar() #passing parameter via query var
        myFont = font.Font(family='Helvetica', size=40, weight='bold')
        width= rt.winfo_screenwidth()
        height= rt.winfo_screenheight()
        rt.geometry("%dx%d" % (width, height))
        rt.title('Main Screen')
        
        self.tkpic = ImageTk.PhotoImage(Image.open("unm.png").resize((400, 250)))
        img = Label(rt, image=self.tkpic).pack(anchor=NW)
        
        def Plot():
            t = Box.get()
            os.system('python3 plot.py '+t)
            
        Pa_Name = Label(rt, text = "Patient Name: ", font = 'Helvetica 30 bold').place(x=500, y=350)
        Box = Entry(rt, font = 'Helvetica 25', textvariable=self.query)
        Box.place(x=800, y=350, width=350, height=50)
        StartButton = Button(rt, text="Start Angle", bg='SpringGreen3', fg='white', font=myFont, command = self.Angle).place(x=600, y=600, width=350, height=200, anchor="center")
        StartPlotButton = Button(rt, text="Start Plot", bg='SpringGreen3', fg='white', font=myFont, command = Plot).place(x=1200, y=600, width=350, height=200, anchor="center")
        Back = Button(rt, text="Back", bg='gold', fg='black', font = 'Helvetica 15 bold', command=rt.destroy).place(x=200, y=700, width=100, height=50, anchor="center")
        
    def popup(self):
        pop = Toplevel(root)
        width= pop.winfo_screenwidth() / 5
        height= pop.winfo_screenheight() / 2
        pop.geometry("%dx%d" % (width, height))
        pop.title('Log In')
        
        def login(username, password):
            l = []
            NoUser = Label(pop, text = "Credentials Not Found", font = 'Helvetica 10 bold')
            UserFound = Label(pop, text = "Welcome "+str(username), font = 'Helvetica 10 bold')
            with open("Users/register.txt", "r") as file:
                for line in file:
                    l.append(line.split())
                for i, credentials in enumerate(l):
                    if username == credentials[0] and password == credentials[1]:
                        NoUser.grid_forget()
                        UserFound.grid(row=8, columnspan=2, sticky='ew',ipady = 20)
                        pop.destroy()
                        self.Openfile()
                        break
                    elif i == len(l)-1:
                        UserFound.grid_forget()
                        NoUser.grid(row=8, columnspan=2, sticky='ew',ipady = 20)
                    else:
                        pass

        def register(username, password):
            l = []
            add_credentials = 0
            USerExists = Label(pop, text = "Username Already Exists", font = 'Helvetica 10 bold')
            RegSuccess = Label(pop, text = "Username Registered Succesfully. Proceed to Login", font = 'Helvetica 10 bold')
            RegNotSuccess = Label(pop, text = "Please Enter Username and Password", font = 'Helvetica 10 bold')
            with open("Users/register.txt", "r") as file:
                for line in file:
                    l.append(line.split())
                for i, credentials in enumerate(l):
                    if username == "":
                        RegNotSuccess.grid(row=8, columnspan=2, sticky='ew',ipady = 20)
                        add_credentials = 0
                        break
                    elif username == credentials[0]:
                        USerExists.grid(row=8, columnspan=2, sticky='ew',ipady = 20)
                        add_credentials = 0
                        break
                    elif i == len(l)-1 and username != credentials[0] and username != "":
                        add_credentials = 1
                        break
            if add_credentials == 1:
                with open("Users/register.txt", "a") as file:
                    file.write(username+'\t' + password)
                USerExists.grid_forget()
                RegNotSuccess.grid_forget()
                RegSuccess.grid(row=8, columnspan=2, sticky='ew',ipady = 20)

        User = Label(pop, text = "User: ", font = 'Helvetica 15 bold')
        User.grid(row=1, column = 0, pady=30)
        UserBox = Entry(pop, font = 'Helvetica 15')
        UserBox.grid(row=1, column = 1)
        
        Password = Label(pop, text = "Password: ", font = 'Helvetica 15 bold')
        Password.grid(row=2, column = 0)
        PassBox = Entry(pop, font = 'Helvetica 15', show="*")
        PassBox.grid(row=2, column = 1)
        
        def Lbutton():
            u = UserBox.get()
            p = PassBox.get()
            login(u,p)
            UserBox.delete(0, END)
            PassBox.delete(0, END)
        OkButton = Button(pop, text="Ok", bg='grey82', fg='black', font='Helvetica 10 bold',command = Lbutton)
        OkButton.grid(row=3, column=1, sticky='w',ipadx = 10, ipady = 6, padx = 30)
        ###############################################REGISTER ENTRIES########################################################
        UserReg = Label(pop, text = "User: ", font = 'Helvetica 15 bold')
        UserBoxReg = Entry(pop, font = 'Helvetica 15')
        
        PasswordReg = Label(pop, text = "Password: ", font = 'Helvetica 15 bold')
        PassBoxReg = Entry(pop, font = 'Helvetica 15', show="*")  

        def Rbutton():
            u = UserBoxReg.get()
            p = PassBoxReg.get()
            register(u,p)
            UserBoxReg.delete(0, END)
            PassBoxReg.delete(0, END)    
        OkButtonReg = Button(pop, text="Ok", bg='grey82', fg='black', font='Helvetica 10 bold',command = Rbutton)

        def ShowLogInEntries():
            UserReg.grid_forget()
            UserBoxReg.grid_forget()
            PasswordReg.grid_forget()
            PassBoxReg.grid_forget()
            OkButtonReg.grid_forget()
            User.grid(row=1, column = 0, pady=20)
            UserBox.grid(row=1, column = 1)
            Password.grid(row=2, column = 0, pady=20)
            PassBox.grid(row=2, column = 1)
            OkButton.grid(row=3, column=1, sticky='w',ipadx = 10, ipady = 6, padx = 30)
            
        def ShowRegEntries():
            User.grid_forget()
            UserBox.grid_forget()
            Password.grid_forget()
            PassBox.grid_forget()
            OkButton.grid_forget()
            UserReg.grid(row=5, column = 0, pady=20)
            UserBoxReg.grid(row=5, column = 1)
            PasswordReg.grid(row=6, column = 0, pady=20)
            PassBoxReg.grid(row=6, column = 1)
            OkButtonReg.grid(row=7, column=1, sticky='w',ipadx = 10, ipady = 6, padx = 30)
                
        LogIn = Button(pop, text="Log In", bg='grey82', fg='black', font='Helvetica 15 bold',command = ShowLogInEntries).grid(row=0, columnspan=2, sticky='ew',ipady = 20)
        Reg = Button(pop, text="Register", bg='brown2', fg='black', font='Helvetica 15 bold',command = ShowRegEntries).grid(row=4, columnspan=2, sticky='ew',ipady = 20)
        
    def Openfile(self):
        def plot(i):
            fig.clear()
            plot1 = fig.add_subplot(111)
            
            # plotting the graph
            plot1.plot(x,y)
            plot1.set_xlabel('Time')
            plot1.set_ylabel('Angle')            
            plot1.set_title(i)
            canvas.draw()

        of = Toplevel(root)
        myFont = font.Font(family='Helvetica', size=15, weight='bold')
        width= of.winfo_screenwidth()
        height= of.winfo_screenheight()
        of.geometry("%dx%d" % (width, height))
        of.title('Open File')
        
        # the figure that will contain the plot
        fig = Figure(figsize = (14, 8), dpi = 100)
        plot1 = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master = of)
        canvas.draw()
        canvas.get_tk_widget().pack()
        toolbar = NavigationToolbar2Tk(canvas, of)
        toolbar.update()
            
        def open_file():
            global x, y
            x = []
            y = []
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
                plot(f[-1])
                
        OpenButton = Button(of, text="Open File", bg='SpringGreen3', fg='white', height= 3, width=10, font=myFont, command = open_file).pack(side = TOP, anchor=NW)
        Back = Button(of, text="Back", bg='gold', fg='black', font=myFont, width=10, command=of.destroy).pack(side = TOP, anchor=NW)
        
    def Angle(self):
        pl = Toplevel(root)
        myFont = font.Font(family='Helvetica', size=15, weight='bold')
        width= pl.winfo_screenwidth()
        height= pl.winfo_screenheight()
        pl.geometry("%dx%d" % (width, height))
        pl.title('Record Data')
        x = []
        y = []
        index = count()
        global rx
        rx = False
        def SaveData():
            Box = messagebox.askquestion('Message', 'Save Data?')
            if Box == 'yes':
                with open("Database/"+self.query.get()+".txt", "a") as f:
                    for xs,ys in zip(x,y):
                        f.write(str(xs)+'\t' + str(ys)+'\n')
                pl.destroy()
            elif Box == 'no':
                pl.destroy()
            else:
                pl.destroy()
            sock.close()
        def b2():
            global rx
            rx = ~rx
            sock.send("s")
            if rx == -1:
                rx_and_echo()
    
        Name = Label(pl, text = "Name: " + self.query.get(), font = 'Helvetica 30').place(x=1000, y=50)
        Back = Button(pl, text="Back", bg='gold', fg='black', font=myFont, command=SaveData).place(x=500, y=700, width=100, height=50, anchor="center")
        Stop = Button(pl, text="Start/Stop", bg='SpringGreen3', fg='white', font=myFont, command=b2).place(x=1200, y=500, width=200, height=100, anchor="center")
                        
        #MAC address of ESP32
        addr = "78:21:84:88:A9:BE"
        service_matches = find_service( address = addr )

        buf_size = 1024;

        if len(service_matches) == 0:
            NoConn= Label(pl, text = "Couldn't find the Tool. Go back, turn on device and start again.", font = 'Helvetica 20').place(x=200, y=800)
            
        else:
            first_match = service_matches[0]
            port = first_match["port"]
            name = first_match["name"]
            host = first_match["host"]

            port=1
            # Create the client socket
            sock=BluetoothSocket(RFCOMM)
            sock.connect((host, port))
        def rx_and_echo():
            #try:
                #angle.place_forget()
            data = sock.recv(buf_size)
            if data:
                d = int(data.decode('utf-8'))
                y.append(d)
                angle = Label(pl, text = str(y[-1]), width = 5, font = 'Helvetica 150').place(x=650, y=500, anchor="center")
            else:
                y.append(0)
            x.append(next(index))
            global rx
            if rx == -1:
                pl.after(4,rx_and_echo)
           # except:
           #     angle = Label(pl, text = "Connection Stopped", font = 'Helvetica 20')
           #     angle.place(x=200, y=800, anchor="center")

root = Tk()
app = Frames()
app.MainScreen(root)
root.mainloop()
