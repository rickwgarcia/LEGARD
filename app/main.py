from core import auth_manager
from ui.auth_ui import LoginApp

if __name__ == "__main__":
    # Ensure file system is ready
    auth_manager.setup_files()
    
    # Launch the UI
    app = LoginApp()
    app.mainloop()