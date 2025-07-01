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
        tk.Label(self, text=f"User: {info[3]}", font='Helvetica 20').grid(row=0, column=2, padx
