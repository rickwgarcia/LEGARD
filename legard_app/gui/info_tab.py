# legard_app/gui/info_tab.py

import tkinter as tk
from PIL import ImageTk, Image
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from config import PLOT_BG_COLOR, DEFAULT_PROFILE_PIC

class InfoTab(tk.Frame):
    """The 'User Info' tab view."""
    def __init__(self, parent, user_manager):
        super().__init__(parent)
        self.user_manager = user_manager
        self._create_widgets()

    def _create_widgets(self):
        # --- Profile Picture ---
        try:
            self.profile_image = ImageTk.PhotoImage(Image.open(DEFAULT_PROFILE_PIC).resize((200, 200)))
            tk.Label(self, image=self.profile_image).grid(row=0, column=0, rowspan=3, padx=20, pady=20)
        except FileNotFoundError:
            tk.Label(self, text="No Image", width=25, height=12, relief="solid").grid(row=0, column=0, rowspan=3, padx=20, pady=20)

        # --- User Details ---
        info = self.user_manager.user_info
        tk.Label(self, text=f"Name: {info[0]} {info[1]}", font='Helvetica 20').grid(row=0, column=1, padx=20, pady=40, sticky="W")
        tk.Label(self, text=f"User: {info[3]}", font='Helvetica 20').grid(row=0, column=2, padx=20, pady=40, sticky="W")
        tk.Label(self, text=f"Gender: {info[2]}", font='Helvetica 20').grid(row=1, column=1, padx=20, sticky="W")

        # --- Polar Plot for Repetitions ---
        self._create_polar_plot()

    def _create_polar_plot(self):
        fig = Figure(figsize=(3, 3), dpi=100)
        fig.patch.set_facecolor(PLOT_BG_COLOR)
        ax = fig.add_subplot(111, polar=True)
        ax.axis('off')

        df = self.user_manager.history_df
        if not df.empty:
            reps_data = [val[0] for val in df['Value']]
            if reps_data:
                max_val = max(reps_data) if reps_data else 0
                lower_limit = 10
                upper_limit = 100
                
                slope = (upper_limit - lower_limit) / max_val if max_val > 0 else 0
                heights = [slope * val + lower_limit for val in reps_data]
                width = 2 * np.pi / len(df.index)
                angles = [i * width for i in range(len(df.index))]

                ax.bar(x=angles, height=heights, width=width, bottom=lower_limit,
                              linewidth=1, edgecolor="black", color="#61a4b2")
                
                # Add labels
                for angle, height, value in zip(angles, heights, reps_data):
                    ax.text(angle, height + 5, str(value), ha='center', va='center', fontdict={'size': 8})

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=2, sticky="E")
