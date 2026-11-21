"""Console-like Tkinter window that live-tails the shared log file.

Run it on its own (``python tkinter_log_viewer.py``) or launch it from the GUI.
"""

import os
import tkinter as tk

from main import LOG_FILE

REFRESH_MS = 1000


def display_log(log_file=LOG_FILE):
    """Open a window showing the log file, refreshed every second."""
    root = tk.Tk()
    root.title("Log Window")
    root.attributes("-topmost", 1)

    frame = tk.Frame(root, bg="black", padx=10, pady=10)
    frame.pack(fill="both", expand=True)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")

    log_text = tk.Text(frame, wrap="word", height=20, width=80, bg="black", fg="white",
                       font=("Consolas", 14), state=tk.DISABLED, yscrollcommand=scrollbar.set)
    log_text.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=log_text.yview)

    last_content = None

    def update_log():
        nonlocal last_content
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            if content != last_content:
                # Keep following the end only if the user hasn't scrolled up.
                at_bottom = log_text.yview()[1] >= 1.0
                log_text.config(state=tk.NORMAL)
                log_text.delete("1.0", tk.END)
                log_text.insert(tk.END, content)
                log_text.config(state=tk.DISABLED)
                if at_bottom:
                    log_text.see(tk.END)
                last_content = content
        root.after(REFRESH_MS, update_log)

    update_log()
    root.mainloop()


if __name__ == "__main__":
    display_log()
