import os
import streamlit as st
from main import download_playlist, postprocess_files, cleanup_log_file

# Initialize Streamlit session state for the log file
if 'log_messages' not in st.session_state:
    st.session_state['log_messages'] = []
if 'log_file' not in st.session_state:
    st.session_state['log_file'] = "shared_log.txt"

# Define the log function
def log(message):
    """Appends a message to the log and updates the session state."""
    if message:
        st.session_state['log_messages'].append(message)
        # Write to the shared log file
        with open("shared_log.txt", "a") as f:
            f.write(message + "\n")
        update_log_area()

# Define the layout
st.title("YouTube Playlist Downloader")

# Input fields for URL and download settings
url = st.text_input("Enter Playlist URL:", "").strip()
destination_folder = st.text_input("Enter Destination Folder:", value=os.path.join(os.path.expanduser('~'), 'Desktop')).strip()
ffmpeg_folder = st.text_input("Enter FFmpeg Folder (optional):", "").strip()
format_choice = st.selectbox("Choose Format", ["mp3", "mp4"], index=0)

# Create a placeholder for the log text area
log_placeholder = st.empty()

def update_log_area():
    """Updates the log area with the latest log messages from the log file."""
    if os.path.exists(st.session_state['log_file']):
        with open(st.session_state['log_file'], 'r') as file:
            log_content = file.read()
        log_placeholder.text(log_content)

def handle_postprocessing():
    """Handles postprocessing if format_choice is mp3."""
    if format_choice == 'mp3':
        postprocess_files(destination_folder)
         
def download_worker():
    """Handles the download process and logs messages."""
    log("Starting the download process...")

    try:
        log(f"Chosen format: {format_choice}")
        log(f"Destination folder: {destination_folder}")
        log(f"Playlist URL: {url}")

        download_playlist(format_choice, destination_folder, url, log_callback=log)
        
        if format_choice == 'mp3':  # Postprocessing is only needed for mp3
            handle_postprocessing()
        log("Download and postprocessing completed successfully.")
    except Exception as e:
        log(f"Download or postprocessing failed: {str(e)}")
    finally:
        cleanup_log_file()

# Start download when the button is pressed
if st.button("Start Download"):
    download_worker()
