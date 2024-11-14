import PySimpleGUI as sg  #Gui library
import urllib.request     #To import images from url
import os
import pandas as pd
from math import *

# For plots
from matplotlib import use as use_agg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

#For BNO sensor
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055

sg.theme('DarkPurple')

i2c = I2C(1)  # Device is /dev/i2c-1
sensor = adafruit_bno055.BNO055_I2C(i2c)
MaxAngle = 0.0
qw = sensor.quaternion[0]
init = 0
while init <= 0 or init >100:
    qw = sensor.quaternion[0]
    if qw is None:
        pass
    else:
        init = round(2*acos(qw)*57.2957795131, 2)

def pack_figure(graph, figure):
    canvas = FigureCanvasTkAgg(figure, graph.Widget)
    plot_widget = canvas.get_tk_widget()
    plot_widget.pack(side='top', fill='both', expand=1)
    return plot_widget

def Plot(index):
    global X, Y
    fig = plt.figure(index)         # Active an existing figure
    ax = plt.gca()                  # Get the current axes
    if X == [] and Y == []:
        x = [0]
        y = [0]
    else:
        x = X
        y = Y
    ax.cla()                        # Clear the current axes
    ax.set_title("Sensor Data")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Weight (lbs)")
    ax.grid()
    plt.xlim([x[-1] - 10, x[-1] + 10])
    plt.ylim([-2, 150])
    plt.plot(x, y)                  # Plot y versus x as lines and/or markers
    fig.canvas.draw()               # Rendor figure into canvas
    
def plot_figure(index, val = 0, t = [], v = [], mx = [], y = []):
    if index == 1:
        title = 'Repetitions per Day' 
        xlab = 'Day'
        ylab = 'Repetitions'
    
    elif index == 2:
        title = 'Usage Time' 
        xlab = 'Day'
        ylab = 'Session Length'
    
    elif index == 3:
        title = 'Resting Time per Session' 
        xlab = 'Day'
        ylab = 'Resting Time'
    elif index == 4:
        title = 'Session Workout' 
        xlab = 'Time(s)'
        ylab = 'Angle (degrees)'
                    
    fig = plt.figure(index)         # Active an existing figure
    ax = plt.gca()                  # Get the current axes
    ax.cla()                        # Clear the current axes
    ax.set_title(title)
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.grid()
    
    if t != []:
        for i,t2 in enumerate(t):
            ax.text(float(t2[1])+0.5, float(max(y)) + 5, 'Rep '+str(i+1))
            ax.text(float(t2[1])+0.5, float(max(y)) + 3, 'Max. Angle '+ str(mx[i][0]))
            ax.text(float(t2[1])+0.5, float(max(y)) + 1, 'Max. Vel. '+max(v[i]))
            ax.axvline(x = float(t2[1]), color = 'b', linestyle = "dashed")
            ax.axvline(x = float(t2[-1]) + 2, color = 'b', linestyle = "dashed")
            
            ax.set_xlim([val, val + 10])
            ax.set_ylim([-1, 25])
            
    plt.plot(y)                  # Plot y versus x as lines and/or markers
    fig.canvas.draw()               # Rendor figure into canvas

def frame(i):
    return [[sg.Graph((320, 240), (0, 0), (320, 240), key=f'Graph{i}')]]

def GetMaxAngle():
    layout=[[sg.Text('Stretch your leg as much\n\tas you can', font=('Arial Bold', 20)), 
             sg.ProgressBar(30, orientation='v', expand_y=True, size=(20, 200),  key='-PBAR-'),
             sg.Button('Start Session')]]
    window =sg.Window("User Window",layout, finalize=True)
    global init, MaxAngle
    while True:
        event, values = window.read(timeout=10)           ###<<------Remove timeout after adding second screen (timeout=10)
        if event == sg.WIN_CLOSED:
            break
        elif event == 'Start Session':
            pass  #Add code to open window and fix -PBAR- error?
        else:
            qw = sensor.quaternion[0]
            if qw is None:
                pass
            else:
                try:
                    a = round(2*acos(qw)*57.2957795131, 2) - init
                    if a > MaxAngle:
                        MaxAngle = a
                    window['-PBAR-'].update(current_count=a)
                except ValueError: 
                    pass
        
################################################## TABS WITH USER INFO ########################################################
def user_window(UserName):
    
    ### Getting User Info........
    UserInfo = []
    UserFiles = os.listdir(f'/home/si/Desktop/LEGARD/app/Users/{UserName}')
    latxt = ''
    var = 0
    df = pd.DataFrame(columns = ['Day', 'Value'])
    with open('/home/si/Desktop/LEGARD/app/Users/' + UserName + '/info.txt', 'r') as file:
        for i, f in enumerate(file):
            if i == 0:
                UserInfo.append(f.split())
            else:
                index = len(df)
                line = f.split()
                Vals = [line[0], [int(line[1]), int(line[2]), int(line[3])]]
                df.loc[index] = Vals
            
    day = len(df) + 1
    DfVal1 = []
    DfVal2 = []
    DfVal3 = []
    
    if len(df) != 0:
            Max = 0
            for f in df['Value']:
                DfVal1.append(f[0])
                DfVal2.append(f[1])
                DfVal3.append(f[2])
                if f[0] > Max:
                    Max = f[0]
                    
    layout1 = [[sg.Image(urllib.request.urlretrieve(r'https://upload.wikimedia.org/wikipedia/commons/9/93/YT_Profile_icon.png')[0]),
                sg.Text('Name: ' + str(UserInfo[0][0]) + ' ' + str(UserInfo[0][1]) + '\nUser: '+ str(UserInfo[0][3]) + '\nGender: ' + str(UserInfo[0][2]), size=(20,5), font=('Arial Bold', 20))]]
    
    layout2=[[sg.Text('Press the Button to set the Target Angle\n and start the routine', font=('Arial Bold', 20))],
             [sg.Button('Set Angle')]]
    
    layout3= [[sg.Combo(UserFiles, font=('Arial Bold', 14), expand_x=True, enable_events=True,  readonly=False, key='-COMBO-')],
              [sg.Button('View', font=('Arial', 15))],
              [sg.Text(latxt, key='-LATEXT-', size=(10,1))],
              [sg.Graph((600, 400), (0, 0), (600, 400), key='Graph')],
              [sg.Slider(range=(0, 500), default_value=var, size=(10, 20), expand_x=True, enable_events=True, orientation='h', 
                         key='Slider')]]
    
    column = [[sg.Frame(f'Graph{i}', frame(i), pad=(0, 0), key=f'FRAME {i}')]for i in range(1, 4)]
    
    layout4 = [[sg.Column(column, scrollable=True, vertical_scroll_only=True, size=(600, 600), key='COLUMN')]]
    
    #Define Layout with Tabs         
    tabgrp = [[sg.TabGroup([[sg.Tab('Personal Details', layout1, title_color='Red',border_width =10,
                                    element_justification= 'center'),
                             sg.Tab('Start Routine', layout2,title_color='Blue'),
                             sg.Tab('Check History', layout3,title_color='Black'),
                             sg.Tab('Analytics', layout4,title_color='Black')]],
                           tab_location='centertop', title_color='Red', tab_background_color='Purple',
                           selected_title_color='Green', selected_background_color='Gray', border_width=5), 
                           sg.Button('Close', size=(15,6), button_color = 'Red')]]  

    
    window =sg.Window("User Window",tabgrp, finalize=True)
    # Initial
    graph = window['Graph']
    graph1 = window['Graph1']
    graph2 = window['Graph2']
    graph3 = window['Graph3']
    plt.ioff()                          # Turn the interactive mode off
    fig = plt.figure(4, figsize = (5,4))                # Create a new figure
    ax = plt.subplot(111)              # Add a subplot to the current figure.
    pack_figure(graph, fig)           # Pack figure under graph
    fig1 = plt.figure(1, figsize = (5,4))                # Create a new figure
    ax1 = plt.subplot(111)              # Add a subplot to the current figure.
    pack_figure(graph1, fig1)           # Pack figure under graph
    fig2 = plt.figure(2, figsize = (5,4))                # Create a new figure
    ax2 = plt.subplot(111)              # Add a subplot to the current figure.
    pack_figure(graph2, fig2)           # Pack figure under graph
    fig3 = plt.figure(3, figsize = (5,4))                # Create a new figure
    ax3 = plt.subplot(111)              # Add a subplot to the current figure.
    pack_figure(graph3, fig3)           # Pack figure under graph
    for i in range(1,4):
        plot_figure(i, y = eval('DfVal' + str(i)))
    
    b = 0
    oneH = False
    while True:
        event, values = window.read()           ###<<------Remove timeout after adding second screen (timeout=10)
        if event == "Close" or event == sg.WIN_CLOSED:
            break
        elif event == sg.TIMEOUT_EVENT:
            for i in range(1,4):
                plot_figure(i, eval('DfVal' + str(i)))
        
        if event == 'Set Angle':
            GetMaxAngle()
        
        if oneH == False:
            b += 1
            window['-PBAR-'].update(current_count=b)
            if b == 100:
                oneH = True
        else:
            b -= 1
            window['-PBAR-'].update(current_count=b)
            if b == 0:
                oneH = False
        
        if event == 'View':
            try:
                comboval = values['-COMBO-']
                with open(f'/home/si/Desktop/LEGARD/app/Users/{UserName}/{comboval}') as f:
                    line2 = [line.split("\t") for line in f]
                found = False
                X = []
                Y = []
                V = []
                MxAng = []
                T = []

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
                            MxAng.append(tst[1].strip('][').split(', '))
                            V.append(tst[2].strip('][').split(', '))
                            T.append(tst[3].strip('][').split(', '))
                            
                plot_figure(4, val=var, t = T, v= V, mx = MxAng, y = Y)              
                window['-LATEXT-'].update('Viewing ' + values['-COMBO-'])
                
            except:
                window['-LATEXT-'].update("No Correct Data" )
            
        if event == 'Slider':
            if values['-COMBO-'] != '':
                var = values[event]
                plot_figure(4, val=var, t = T, v= V, mx = MxAng, y = Y)
                
    window.close()

################################################## LOG IN AND REGISTRATION ####################################################
def LoginWindow():
    txt = ''
    layout = [[sg.Button("Log in", size=(50,2), font=('Arial Bold', 20))],
              [sg.Text('User', size=(10,1)),sg.Input('',key='usr')],
              [sg.Text('Password', size=(10,1)),sg.Input('',key='pass',password_char='*')],
              [sg.Button("Ok", key="login", size=(10,2))],
              [sg.Button("Register", size=(50,2), font=('Arial Bold', 20))],
              [sg.Text('First Name', size=(10,1)),sg.Input('',key='reg_nme')],
              [sg.Text('Last Name', size=(10,1)),sg.Input('',key='reg_lnm')],
              [sg.Text('User', size=(10,1)),sg.Input('',key='reg_usr')],
              [sg.Text('Password', size=(10,1)),sg.Input('',key='reg_pass',password_char='*')],
              [sg.T("         "), sg.Radio('Male', "RADIO1", default=False, key="-Male-"), sg.T("         "), 
               sg.Radio('Female', "RADIO1", default=False, key="-Female-")],
              [sg.Button("Ok", key="register", size=(10,2))],
              [sg.Text(txt, key='-TEXT-', font=('Arial Bold', 10), expand_x=True, justification='center')]]
    window = sg.Window("Log in Window", layout, element_justification='c')

    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif event == "login":
            l = []
            with open("/home/si/Desktop/LEGARD/app/Users/register.txt", "r") as file:#####<<<<<-----Possible change in path
                for line in file:
                    l.append(line.split())
                for i, credentials in enumerate(l):
                    if values['usr'] == credentials[0] and values['pass'] == credentials[1]:
                        window['usr'].update('')
                        window['pass'].update('')
                        window['-TEXT-'].update("Welcome " + values['usr'])
                        user_window(credentials[0])
                        break
                    elif i == len(l) - 1:
                        window['usr'].update('')
                        window['pass'].update('')
                        window['-TEXT-'].update("Credentials Not Found")
                    else:
                        pass
        elif event == 'register':
            l = []
            add_credentials = 0
            if values['reg_nme'] == "" or values['reg_lnm'] == "" or values['reg_usr'] == "" or values['reg_pass'] == "" or (values['-Male-'] == False and values['-Female-'] == False): 
                window['-TEXT-'].update("Fill out all empty spaces")
            else:
                with open("/home/si/Desktop/LEGARD/app/Users/register.txt", "r") as file:#####<<<<<-----Possible change in path
                    for line in file:
                        l.append(line.split())
                    for i, credentials in enumerate(l):
                        if values['reg_usr'] == credentials[0]:
                            window['-TEXT-'].update("User name already exits")
                            break
                        elif i == len(l) - 1 and values['reg_usr'] != credentials[0]:
                            add_credentials = 1
                            break
            if add_credentials == 1:
                with open("/home/si/Desktop/LEGARD/app/Users/register.txt", "a") as file:#####<<<<<-----Possible change in path
                    file.write(values['reg_usr'] + '\t' + values['reg_pass'] + '\n')
                os.mkdir("/home/si/Desktop/LEGARD/app/Users/" + values['reg_usr'])
                with open("/home/si/Desktop/LEGARD/app/Users/" + values['reg_usr'] + "/info.txt", "a") as file:
                    if values['-Male-'] == True:
                        Gender = "Male"
                    else:
                        Gender = "Female"
                    file.write(values['reg_nme'] + '\t' + values['reg_lnm'] + '\t' + Gender + '\t' + values['reg_usr'] + '\t' + values['reg_pass'] + '\n')
                    window['reg_nme'].update('')
                    window['reg_lnm'].update('')
                    window['reg_usr'].update('')
                    window['reg_pass'].update('')
                    window['-TEXT-'].update("User registered, proceed to log in")
    window.close()
if __name__ == "__main__":
    LoginWindow()