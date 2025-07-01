# legard_app/gui/main_tabs.py

from tkinter import ttk
from gui.info_tab import InfoTab
from gui.routine_tab import RoutineTab
from gui.history_tab import HistoryTab
from gui.analytics_tab import AnalyticsTab

class MainTabs(ttk.Notebook):
    """The main notebook widget containing all application tabs."""
    def __init__(self, parent, user_manager, start_routine_callback, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Create instances of each tab
        self.info_tab = InfoTab(self, user_manager)
        self.routine_tab = RoutineTab(self, start_routine_callback)
        self.history_tab = HistoryTab(self, user_manager)
        self.analytics_tab = AnalyticsTab(self, user_manager)
        
        # Add tabs to the notebook
        self.add(self.info_tab, text='User Info')
        self.add(self.routine_tab, text='Start Routine')
        self.add(self.history_tab, text='Check History')
        self.add(self.analytics_tab, text='Analytics')
