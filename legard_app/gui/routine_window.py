# legard_app/gui/routine_window.py

import tkinter as tk
from tkinter import ttk, messagebox, font
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

class RoutineWindow(tk.Toplevel):
    """A Toplevel window for displaying the real-time exercise routine."""
    def __init__(self, parent, shared_state, on_close_callback):
        super().__init__(parent)
        self.shared_state = shared_state
        self.on_close = on_close_callback

        self.title("Routine in Progress")
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry(f"{width}x{height}+0+0")
        
        self.protocol("WM_DELETE_WINDOW", self._handle_close)
        
        self._create_widgets()
        self.ani = FuncAnimation(self.fig, self.animate, interval=500, blit=False)

    def _create_widgets(self):
        # --- UI Variables ---
        self.status_text = tk.StringVar(value="Starting routine...")
        self.message_text = tk.StringVar(value="Prepare to start.")

        # --- Fonts ---
        myFont = font.Font(family='Helvetica', size=20, weight='bold')

        # --- Top Info Labels ---
        info_frame = tk.Frame(self)
        info_frame.pack(fill='x', pady=10)
        tk.Label(info_frame, textvariable=self.status_text, font=myFont).pack(side='left', padx=20)
        tk.Label(info_frame, textvariable=self.message_text, font=myFont, bg='lightblue').pack(side='right', padx=20)

        # --- Matplotlib Plot ---
        self.fig = Figure(figsize=(12, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(pady=10)
        
        # --- Stop Button ---
        ttk.Button(self, text="Stop Routine", command=self._handle_close, style="C.TButton").pack(pady=20)
        ttk.Style().configure("C.TButton", font=("Helvetica", 16), padding=20, background='red')

    def animate(self, i):
        """Updates the plot and labels with data from the shared state."""
        # Update labels
        self.status_text.set(f"Set: {self.shared_state['current_set']} | Rep: {self.shared_state['rep_count']}")
        self.message_text.set(self.shared_state['message'])
        
        # Update plot
        x = self.shared_state['x_data']
        y1 = self.shared_state['y1_data']
        y2 = self.shared_state['y2_data']

        if not x: return
        
        self.ax.clear()
        self.ax.plot(x, y1, label=f"Leg Angle: {y1[-1]:.1f}°")
        self.ax.plot(x, y2, label=f"Knee Angle: {y2[-1]:.1f}°")
        
        self.ax.set_title("Real-Time Angle Tracking")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Angle (°)")
        self.ax.legend(loc='upper left')
        self.ax.grid(True)
        
        # Auto-scroll x-axis
        if len(x) > 20:
            self.ax.set_xlim(x[-20], x[-1] + 5)

    def _handle_close(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to stop the routine and save the data?"):
            self.ani.event_source.stop() # Stop animation
            self.on_close() # Trigger callback in app.py
            self.destroy()
