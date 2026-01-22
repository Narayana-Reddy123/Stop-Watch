"""
Python Stopwatch (GUI)

Features:
- Start/Pause toggle
- Reset
- Lap with lap list (shows total time and split since previous lap)
- Keyboard shortcuts: Space (Start/Pause), R (Reset), L (Lap)

Run:
  python stopwatch.py
"""

import tkinter as tk
from tkinter import ttk
import time


def format_time(seconds: float) -> str:
    """Format seconds as MM:SS.mmm"""
    if seconds < 0:
        seconds = 0.0
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{minutes:02d}:{secs:02d}.{millis:03d}"


class StopwatchApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Python Stopwatch")
        self.root.minsize(420, 320)
        try:
            # Improve default scaling on hi-dpi displays
            self.root.tk.call("tk", "scaling", 1.2)
        except tk.TclError:
            pass

        # State
        self.running = False
        self._start_perf = 0.0           # perf_counter when last started
        self._accum_elapsed = 0.0        # accumulated time while paused
        self._last_lap_total = 0.0       # total time at last lap
        self._tick_interval_ms = 33      # ~30 FPS updates

        # Styles
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Time.TLabel", font=("Segoe UI", 48, "bold"))
        style.configure("Controls.TButton", font=("Segoe UI", 11))

        # Layout
        container = ttk.Frame(root, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        self.time_label = ttk.Label(container, text=format_time(0.0), style="Time.TLabel")
        self.time_label.pack(pady=(8, 16))

        btns = ttk.Frame(container)
        btns.pack(pady=4)

        self.start_pause_btn = ttk.Button(btns, text="Start", style="Controls.TButton", command=self.toggle_start_pause)
        self.start_pause_btn.grid(row=0, column=0, padx=6, pady=6, sticky="ew")

        reset_btn = ttk.Button(btns, text="Reset", style="Controls.TButton", command=self.reset)
        reset_btn.grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        lap_btn = ttk.Button(btns, text="Lap", style="Controls.TButton", command=self.lap)
        lap_btn.grid(row=0, column=2, padx=6, pady=6, sticky="ew")

        for i in range(3):
            btns.grid_columnconfigure(i, weight=1)

        # Lap list
        lap_container = ttk.Frame(container)
        lap_container.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        lap_label = ttk.Label(lap_container, text="Laps")
        lap_label.pack(anchor="w")

        self.lap_list = tk.Listbox(lap_container, font=("Consolas", 11))
        self.lap_list.pack(fill=tk.BOTH, expand=True)

        # Key bindings
        root.bind("<space>", lambda e: self.toggle_start_pause())
        root.bind("<KeyPress-r>", lambda e: self.reset())
        root.bind("<KeyPress-l>", lambda e: self.lap())

        # Start update loop
        self._schedule_tick()

    def _now(self) -> float:
        return time.perf_counter()

    def _current_total(self) -> float:
        if self.running:
            return self._accum_elapsed + (self._now() - self._start_perf)
        return self._accum_elapsed

    def _schedule_tick(self):
        self._update_time_label()
        self.root.after(self._tick_interval_ms, self._schedule_tick)

    def _update_time_label(self):
        total = self._current_total()
        self.time_label.config(text=format_time(total))

    def start(self):
        if not self.running:
            self.running = True
            self._start_perf = self._now()
            self.start_pause_btn.config(text="Pause")

    def pause(self):
        if self.running:
            self._accum_elapsed += self._now() - self._start_perf
            self.running = False
            self.start_pause_btn.config(text="Start")

    def toggle_start_pause(self):
        if self.running:
            self.pause()
        else:
            self.start()

    def reset(self):
        self.running = False
        self._accum_elapsed = 0.0
        self._last_lap_total = 0.0
        self.start_pause_btn.config(text="Start")
        self.lap_list.delete(0, tk.END)
        self._update_time_label()

    def lap(self):
        total = self._current_total()
        lap_number = self.lap_list.size() + 1
        split = total - self._last_lap_total if lap_number > 1 else total
        self._last_lap_total = total
        self.lap_list.insert(tk.END, f"Lap {lap_number:02d} | Total: {format_time(total)} | Split: {format_time(split)}")
        # Auto-scroll to last lap
        self.lap_list.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = StopwatchApp(root)
    root.mainloop()