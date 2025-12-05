from core import auth_manager
from ui.auth_ui import LoginApp

if __name__ == "__main__":
    """
    Main entry point for the application.

    This script initializes the necessary file structure for the authentication 
    manager and then launches the graphical user interface (GUI) for the 
    login application.
    """
    auth_manager.setup_files()
    app = LoginApp()
    app.mainloop()