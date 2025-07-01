# legard_app/main.py

import tkinter as tk
from gui.app import App

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = App(root)
        # Set the main closing protocol
        root.protocol("WM_DELETE_WINDOW", app.on_app_close)
        root.mainloop()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Clean up GPIO in case of a crash
        try:
            from hardware.gpio_handler import GPIOHandler
            GPIOHandler().cleanup()
        except Exception as gpio_e:
            print(f"Could not run GPIO cleanup: {gpio_e}")
