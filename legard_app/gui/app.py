# legard_app/gui/app.py

import tkinter as tk
from multiprocessing import Process, Manager
from gui.login_frame import LoginFrame
from gui.main_tabs import MainTabs
from gui.routine_window import RoutineWindow
from hardware.gpio_handler import GPIOHandler
from logic.routine_logic import RoutineLogic

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("LEGARD Therapy System")
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        self.root.geometry(f"{width}x{height}")
        
        self.user_manager = None
        self.current_frame = None
        
        self.gpio_handler = GPIOHandler()

        # Shared state for multiprocessing
        self.manager = Manager()
        self.shared_state = None
        self.routine_process = None

        self._show_login()

    def _clear_root(self):
        """Clears all widgets from the root window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def _show_login(self):
        self._clear_root()
        self.current_frame = LoginFrame(self.root, on_login_success=self.on_login)
        self.current_frame.pack(fill="both", expand=True)

    def on_login(self, user_manager):
        """Callback executed on successful login."""
        self.user_manager = user_manager
        self.root.after(1000, self._show_main_app) # Delay to show welcome message

    def _show_main_app(self):
        self._clear_root()
        self.main_tabs = MainTabs(self.root, self.user_manager, self._start_routine)
        self.main_tabs.pack(expand=1, fill="both")
        
        # Setup GPIO for the routine tab's stretch selection
        self._setup_stretch_selection_gpio()

    def _setup_stretch_selection_gpio(self):
        # Create a mapping from pin name to the callback function
        # e.g., 'stretch_1' -> lambda event: self.main_tabs.routine_tab.update_stretch_level(1)
        callbacks = {f'stretch_{i}': (lambda lvl=i: lambda e: self.main_tabs.routine_tab.update_stretch_level(lvl))() for i in range(1, 11)}
        self.gpio_handler.setup_pins_for_stretch_selection(callbacks)

    def _start_routine(self, max_stretch_level):
        """Initializes and starts the exercise routine process and window."""
        print(f"Starting routine with max stretch level: {max_stretch_level}")

        # 1. Create shared state dictionary
        self.shared_state = self.manager.dict({
            'running': True,
            'paused_for_rest': False,
            'rep_in_progress': False,
            'message': 'Starting...',
            'current_set': 1,
            'rep_count': 0,
            'current_rep_max_angle': 0,
            'initial_angle1': 0,
            'initial_angle2': 0,
            'x_data': self.manager.list(),
            'y1_data': self.manager.list(),
            'y2_data': self.manager.list(),
        })

        # 2. Instantiate the logic class
        self.routine_logic = RoutineLogic(self.shared_state)
        
        # 3. Start the process
        self.routine_process = Process(target=self.routine_logic.run)
        self.routine_process.start()

        # 4. Show the routine window
        self.routine_window = RoutineWindow(self.root, self.shared_state, self._on_routine_close)

    def _on_routine_close(self):
        """Callback when the routine window is closed by the user."""
        print("Stopping routine...")
        
        # Signal the process to stop
        if self.shared_state:
            self.shared_state['running'] = False

        # Wait for the process to finish
        if self.routine_process and self.routine_process.is_alive():
            self.routine_process.join(timeout=2)
            if self.routine_process.is_alive():
                self.routine_process.terminate() # Force terminate if it doesn't close
        
        print("Routine process stopped.")
        
        # Save data here
        # self.user_manager.save_session(...)
        
        self.gpio_handler.cleanup() # Important!
        # Re-initialize GPIO for the main screen
        self._setup_stretch_selection_gpio()

    def on_app_close(self):
        """Cleanup actions when the entire application is closed."""
        print("Application closing. Cleaning up...")
        if self.shared_state and self.routine_process:
             self._on_routine_close() # Ensure routine is stopped properly
        else:
            self.gpio_handler.cleanup()
        self.root.destroy()
