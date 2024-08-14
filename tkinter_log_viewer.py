import tkinter as tk
import os

def display_log():
    """Function to display the log file content in a Tkinter window."""
    def update_log():
        """Update the log window with new content."""
        if not continue_running:
            return  # Exit the function if not running

        if os.path.exists(log_file):
            with open(log_file, 'r') as file:
                log_content = file.read()
            log_text.config(state=tk.NORMAL)  # Allow editing to insert new content
            log_text.delete(1.0, tk.END)  # Clear the current content
            log_text.insert(tk.END, log_content)  # Insert new content
            log_text.config(state=tk.DISABLED)  # Disable editing
            
            # Auto-scroll to the bottom if needed
            if auto_scroll:
                log_text.yview(tk.END)
        
        # Continue updating every 1000ms (1 second)
        if continue_running:
            root.after(1000, update_log)
    
    def on_closing():
        """Handle window close event."""
        global continue_running
        continue_running = False
        root.destroy()

    def on_scroll(event):
        """Handle the scroll event to toggle auto-scroll."""
        global auto_scroll
        # Check if the user is scrolling up or down
        if event.delta > 0:  # Scrolled up
            auto_scroll = False
        elif event.delta < 0:  # Scrolled down
            auto_scroll = True

    def check_scroll():
        """Check if the user is at the bottom of the text widget."""
        global auto_scroll
        # Enable auto-scroll if at the bottom
        if log_text.yview()[1] >= 1.0:  # Check if at the bottom
            auto_scroll = True

    # Create a new Tkinter window
    root = tk.Tk()
    root.title("Log Window")
    
    # Ensure the window stays on top
    root.attributes('-topmost', 1)
    
    # Flag to control the update loop
    global continue_running
    continue_running = True

    # Flag to control auto-scrolling
    global auto_scroll
    auto_scroll = True
    
    # Create a frame for better layout management
    frame = tk.Frame(root, bg='black', padx=10, pady=10)
    frame.pack(fill='both', expand=True)
    
    # Create a Text widget to display the log
    log_text = tk.Text(frame, wrap='word', height=20, width=80,
                       bg='black', fg='white', font=('Consolas', 14))  # Larger monospaced font
    log_text.pack(fill='both', expand=True)
    
    # Make the text area non-editable
    log_text.config(state=tk.DISABLED)
    
    # Bind the scroll event to detect user scroll
    log_text.bind_all("<MouseWheel>", on_scroll)
    
    # Check if user is at the bottom initially
    log_text.bind("<Configure>", lambda e: check_scroll())
    
    # Call update_log to start updating the Text widget
    update_log()
    
    # Bind the window close event to stop updates
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the Tkinter event loop
    root.mainloop()

# Specify the path to the log file
log_file = "shared_log.txt"
