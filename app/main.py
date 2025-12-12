from core import auth_manager
from ui.auth_ui import LoginApp

# ---------------------
# File: main.py
# Author: Ricardo Garcia, ricardo.garcia@cosmiac.org
# Last Modified: 2025-12-12
# Version: 2.0.0
# ---------------------

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