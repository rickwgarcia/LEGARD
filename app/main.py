# main.py
import tkinter as tk
from gui.login import LoginWindow
from gui.main_screen import MainScreen

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window during login

    def on_login_success(username):
        root.deiconify()  # Show the main window
        app = MainScreen(root, username)
        root.protocol("WM_DELETE_WINDOW", app.on_close)

    login_window = LoginWindow(root, on_login_success)
    root.mainloop()

if __name__ == '__main__':
    main()

