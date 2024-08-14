import os
import streamlit as st
from main import download_playlist, cleanup_log_file, log_to_file
import tkinter as tk
from tkinter import filedialog
from tkinter_log_viewer import display_log

# Initialize Streamlit session state
if 'destination_folder' not in st.session_state:
    st.session_state['destination_folder'] = os.path.join(os.path.expanduser('~'), 'Desktop')
    cleanup_log_file()

# Directory picker - tkinter Integration
root = tk.Tk()
root.withdraw()
root.wm_attributes('-topmost', 1)

def update_label_area(text):
    st.session_state['destination_folder'] = text

# Define the layout
st.title("YouTube Playlist Downloader", help="Brought to you by Prototype_S1")

# Input fields for URL and download settings
url = st.text_input("Enter Playlist URL:", "")
dir_placeholder = st.empty()
destination_folder = dir_placeholder.text_input("Enter Destination Folder:", value=st.session_state['destination_folder'])
ffmpeg_folder = st.text_input("Enter FFmpeg Folder (optional, leave blank if set up in the system PATH):", "")
format_choice = st.selectbox("Choose Format", ["mp3", "mp4"], index=0)
browse = st.button("Browse Directory")
show_logger = st.button("Show log")
start = st.button("Start Download", type='primary')
progress_placeholder = st.empty()
log_placeholder = st.empty()  # Create a placeholder for the log area

def download_worker():
    """Handles the download process and logs messages."""
    try:
        download_playlist(format_choice, destination_folder, url, ffmpeg_folder)
    except Exception as e:
        log_to_file(f"Download or postprocessing failed: {str(e)}")
        st.error(e)

if start:
    download_worker()

if show_logger:
    display_log()

if browse:
    dirname = filedialog.askdirectory(master=root)
    if dirname:
        destination_folder = dirname
        update_label_area(dirname)
        # Update the placeholder with the new directory
        dir_placeholder.text_input("Enter Destination Folder:", value=dirname)
        st.info(f"Targeted directory : {destination_folder}", icon="📂")
