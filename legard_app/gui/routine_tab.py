# legard_app/gui/routine_tab.py

import tkinter as tk

class RoutineTab(tk.Frame):
    """The 'Start Routine' tab view."""
    def __init__(self, parent, start_routine_callback):
        super().__init__(parent)
        self.start_routine_callback = start_routine_callback
        
        self.max_stretch_level = 0
        self.stretch_labels = {}
        
        self._create_widgets()

    def _create_widgets(self):
        # --- Main Layout Frames ---
        container = tk.Frame(self)
        container.pack(expand=True)
        
        left_frame = tk.Frame(container)
        left_frame.pack(side='left', padx=100, pady=50)
        
        right_frame = tk.Frame(container)
        right_frame.pack(side='left', padx=50)

        # --- Left Frame: Instructions and Start Button ---
        tk.Label(left_frame, text="Stretch your leg to the\nhighest comfortable level.\nThen, click Start.", font='Helvetica 20').pack(pady=20)
        tk.Button(left_frame, text="Start Routine", bg='SpringGreen3', fg='white', font='Helvetica 20', width=15, height=5,
                  command=lambda: self.start_routine_callback(self.max_stretch_level)).pack()

        # --- Right Frame: Stretch Level Indicators ---
        tk.Label(right_frame, text="Stretch Levels", font='Helvetica 16 bold').grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Create labels for levels 10 down to 1
        for i in range(10, 0, -1):
            row = 10 - i + 1 # Grid row starts from 1
            tk.Label(right_frame, text=f"Level {i}", font='Helvetica 14').grid(row=row, column=0, sticky='w', padx=10)
            lbl = tk.Label(right_frame, text=" ", bg='grey40', width=10, height=1, relief='sunken')
            lbl.grid(row=row, column=1, pady=2)
            self.stretch_labels[i] = lbl

    def update_stretch_level(self, level):
        """Callback for GPIO events to update the UI."""
        if level > self.max_stretch_level:
            self.max_stretch_level = level
        
        print(f"Stretch level {level} reached. Max is now {self.max_stretch_level}.")
        
        # Light up all levels up to the current one
        for i in range(1, 11):
            if i <= level:
                if i in self.stretch_labels:
                    self.stretch_labels[i].config(bg='SpringGreen3')
            else:
                 self.stretch_labels[i].config(bg='grey40') # Reset higher levels if needed
