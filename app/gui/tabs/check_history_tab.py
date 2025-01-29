# gui/tabs/check_history_tab.py
import tkinter as tk
from tkinter import ttk
import os
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Slider

class CheckHistoryTab:
    def __init__(self, parent, username):
        self.frame = tk.Frame(parent)
        self.username = username
        self.setup_ui()
    
    def setup_ui(self):
        user_path = os.path.join("Users", self.username)
        dir_list = os.listdir(user_path) if os.path.exists(user_path) else []
        
        def show():
            selected_file = clicked.get()
            if selected_file == "Select File to View" or not selected_file:
                label.config(text="No Correct Data")
                return
            label.config(text=f"Viewing {selected_file}")
            file_path = os.path.join(user_path, selected_file)
            try:
                with open(file_path, "r") as f:
                    lines = f.readlines()
                # Process the file data
                X, Y, Y2, V, MxAng1, T = [], [], [], [], [], []
                found = False
                for line in lines:
                    parts = line.strip().split("\t")
                    if "X(Time)" in parts:
                        found = True
                        continue
                    if found:
                        X.append(float(parts[0]))
                        Y.append(float(parts[1]))
                        if len(parts) > 2:
                            Y2.append(float(parts[2]))
                    else:
                        if len(parts) >= 4:
                            MxAng1.append(parts[1])
                            V.append(parts[2])
                            T.append(parts[3])
                # Clear previous plot
                bx.cla()
                bx.plot(X, Y, color='b')
                if Y2:
                    bx.plot(X, Y2, color='r')
                # Add annotations
                for i, t in enumerate(T):
                    bx.text(float(t)+0.5, max(Y)+7, f'Rep {i+1}')
                    bx.text(float(t)+0.5, max(Y)+5, f'Max. Angle {MxAng1[i]}')
                    if i < len(V):
                        bx.text(float(t)+0.5, max(Y)+3, f'Max. Vel. {V[i]}')
                    bx.axvline(x=float(t), color='b', linestyle="dashed")
                update(1)
            except Exception as e:
                label.config(text="Error Loading Data")
                print(e)
    
        def update(val):
            pos = s_time.val
            bx.axis([pos, pos + 10, 0, 30])
            fig_canvas.draw_idle()
    
        # Dropdown menu options
        options = dir_list if dir_list else ["No Files"]
        clicked = tk.StringVar()
        clicked.set("Select File to View")
    
        # Create Dropdown menu
        drop = tk.OptionMenu(self.frame, clicked, *options)
        drop.grid(row=0, columnspan=5, pady=10)
    
        # Create button to view selected file
        view_button = tk.Button(self.frame, text="View", command=show)
        view_button.grid(row=1, columnspan=5)
    
        # Label to display status
        label = tk.Label(self.frame, text=" ")
        label.grid(row=2, columnspan=5)
    
        # Plot Area
        fig = plt.Figure(figsize=(8, 3))
        fig_canvas = FigureCanvasTkAgg(fig, self.frame)
        fig_canvas.get_tk_widget().grid(row=3, columnspan=5)
        bx = fig.add_subplot(111)
        fig.subplots_adjust(bottom=0.25)
    
        # Slider for time
        bx_time = fig.add_axes([0.12, 0.1, 0.78, 0.03])
        s_time = Slider(bx_time, 'Time', 0, 1000, valinit=0)
        s_time.on_changed(update)

