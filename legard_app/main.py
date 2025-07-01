# legard_app/main.py (Temporary debugging version)

import tkinter as tk
from gui.app import App

# The try/except block has been removed to get a more detailed error message.

root = tk.Tk()
app = App(root)
root.protocol("WM_DELETE_WINDOW", app.on_app_close)
root.mainloop()
