# gui/tabs/user_info_tab.py
import tkinter as tk
from PIL import ImageTk, Image
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class UserInfoTab:
    def __init__(self, parent, user, df):
        self.frame = tk.Frame(parent)
        self.user = user
        self.df = df
        self.setup_ui()
    
    def setup_ui(self):
        # Profile Picture
        try:
            self.tkpic = ImageTk.PhotoImage(Image.open("prof_pic.png").resize((200, 200)))
            tk.Label(self.frame, image=self.tkpic).grid(rowspan=3, column=0)
        except Exception as e:
            tk.Label(self.frame, text="No Image Found").grid(rowspan=3, column=0)
        
        # User Information Labels
        if self.user:
            tk.Label(self.frame, text=f"Name: {self.user[0]} {self.user[1]}", font='Helvetica 20').grid(row=0, column=1, padx=20, pady=40, sticky="W")
            tk.Label(self.frame, text=f"User: {self.user[3]}", font='Helvetica 20').grid(row=0, column=2, padx=20, pady=40, sticky="W")
            tk.Label(self.frame, text=f"Gender: {self.user[2]}", font='Helvetica 20').grid(row=1, column=1, padx=20, sticky="W")
        else:
            tk.Label(self.frame, text="User: Guest", font='Helvetica 20').grid(row=0, column=1, padx=20, pady=40, sticky="W")
        
        # Polar Plot of Repetitions
        fig = Figure(figsize=(3, 2), dpi=100)
        fig.patch.set_facecolor('#E0E0E0')
        ax = fig.add_subplot(111, polar=True)
        ax.axis('off')
        canvas = FigureCanvasTkAgg(fig, master=self.frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=2, sticky="E")
        lowerLimit = 30
        DfVal1 = []
        DfVal2 = []
        DfVal3 = []

        if not self.df.empty:
            # Compute max and min in the dataset
            max1 = self.df['Value'].apply(lambda x: x[0]).max()
            DfVal1 = self.df['Value'].apply(lambda x: x[0]).tolist()
            DfVal2 = self.df['Value'].apply(lambda x: x[1]).tolist()
            DfVal3 = self.df['Value'].apply(lambda x: x[2]).tolist()

            # Heights
            slope = (100 - lowerLimit) / max1 if max1 != 0 else 1
            heights = [slope * val + lowerLimit for val in DfVal1]

            # Width and angles
            width = 2 * np.pi / len(self.df.index)
            angles = [i * width for i in range(1, len(self.df.index) + 1)]

            # Draw bars
            bars = ax.bar(
                x=angles,
                height=heights,
                width=width,
                bottom=lowerLimit,
                linewidth=2,
                edgecolor="black",
                color="#61a4b2"
            )

            # Add labels
            labelPadding = 4
            for bar, angle, height, value in zip(bars, angles, heights, DfVal1):
                rotation = np.rad2deg(angle)
                alignment = "left"
                if np.pi/2 <= angle < 3*np.pi/2:
                    alignment = "right"
                    rotation += 180
                ax.text(
                    x=angle,
                    y=lowerLimit + bar.get_height() + labelPadding,
                    s=str(value),
                    ha=alignment,
                    va='center',
                    rotation=rotation,
                    rotation_mode="anchor"
                )

