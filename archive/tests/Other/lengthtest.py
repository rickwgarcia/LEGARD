from tkinter import *
from tkinter import ttk
import RPi.GPIO as GPIO
        
class Frames(object):
                
    def MainScreen(self,root):
        width= root.winfo_screenwidth()
        height= root.winfo_screenheight()
        root.geometry("%dx%d" % (width, height))
        root.title('Main Screen')
        tabsystem = ttk.Notebook(root)
        
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
        

        def button(channel):
            Label(tab2, text = " ", bg='SpringGreen3', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=9,column=1)
            
        GPIO.add_event_detect(ButtonPin, GPIO.RISING,callback=button)

        def button2(channel):
            Label(tab2, text = " ", bg='SpringGreen3', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=8,column=1)
            
        GPIO.add_event_detect(ButtonPin2, GPIO.RISING,callback=button2)
        
        def button3(channel):
            Label(tab2, text = " ", bg='SpringGreen3', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=7,column=1)
            
        GPIO.add_event_detect(ButtonPin3, GPIO.RISING,callback=button3)
        
        def button4(channel):
            Label(tab2, text = " ", bg='SpringGreen3', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=6,column=1)
            
        GPIO.add_event_detect(ButtonPin4, GPIO.RISING,callback=button4)
        
        def button5(channel):
            Label(tab2, text = " ", bg='SpringGreen3', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=5,column=1)
            
        GPIO.add_event_detect(ButtonPin5, GPIO.RISING,callback=button5)
        
        def button6(channel):
            Label(tab2, text = " ", bg='SpringGreen3', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=4,column=1)
            
        GPIO.add_event_detect(ButtonPin6, GPIO.RISING,callback=button6)

        def button7(channel):
            Label(tab2, text = " ", bg='SpringGreen3', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=3,column=1)
            
        GPIO.add_event_detect(ButtonPin7, GPIO.RISING,callback=button7)
        
        def button8(channel):
            Label(tab2, text = " ", bg='SpringGreen3', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=2,column=1)
            
        GPIO.add_event_detect(ButtonPin8, GPIO.RISING,callback=button8)
        
        def button9(channel):
            Label(tab2, text = " ", bg='SpringGreen3', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=1,column=1)
            
        GPIO.add_event_detect(ButtonPin9, GPIO.RISING,callback=button9)
        
        def button10(channel):
            Label(tab2, text = " ", bg='SpringGreen3', fg='white', font = 'Helvetica 20', height = 1, width=10).grid(row=0,column=1)
            
        GPIO.add_event_detect(ButtonPin10, GPIO.RISING,callback=button10)
        
        # Create new tabs using Frame widget
        tab1 = Frame(tabsystem)
        tab2 = Frame(tabsystem)

        tabsystem.add(tab1, text='User Info')
        tabsystem.add(tab2, text='Start Routine')
        tabsystem.pack(expand=1, fill="both")
        
        ################################################TAB 1 STUFF############################################################################
        Label(tab1,text="Name: ", font = 'Helvetica 20').grid(row=0,column=1,padx=20,pady=40,sticky="W")
        Label(tab1,text="User: ", font = 'Helvetica 20').grid(row=0,column=2,padx=20,pady=40,sticky="W")
        Label(tab1,text="Gender: ", font = 'Helvetica 20').grid(row=1,column=1,padx=20,sticky="W")
        
        ################################################TAB 2 STUFF############################################################################        label2nd = Label(tab2, text="Now we are able to see another tab")
        Label(tab2,text="Stretch your leg the \n highest you can. Then,\n click Start.", font = 'Helvetica 20').grid(rowspan=10,column=0,padx=100)
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
        
root = Tk()
app = Frames()
app.MainScreen(root)
root.mainloop()


