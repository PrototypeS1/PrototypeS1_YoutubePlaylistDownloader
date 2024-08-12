import os
import streamlit as st
from main import download_playlist
import tkinter as tk
from tkinter import filedialog

# Initialize Streamlit session state
if 'log_messages' not in st.session_state:
    st.session_state['log_messages'] = []
if 'destination_folder' not in st.session_state:
    st.session_state['destination_folder'] = os.path.join(os.path.expanduser('~'), 'Desktop')

# Directory picker - tkinter Integration
root = tk.Tk()
root.withdraw()
root.wm_attributes('-topmost', 1)

def update_label_area(text):
    st.session_state['destination_folder'] = text

def update_log_area():
    """Updates the log area with the latest log messages from the log file."""
    if os.path.exists("shared_log.txt"):
        with open("shared_log.txt", 'r') as file:
            log_content = file.read()
        log_placeholder.text(log_content)

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
url = st.text_input("Enter Playlist URL:", "")
dir_placeholder = st.empty()
destination_folder = dir_placeholder.text_input("Enter Destination Folder:", value=st.session_state['destination_folder'])
ffmpeg_folder = st.text_input("Enter FFmpeg Folder (optional):", "")
format_choice = st.selectbox("Choose Format", ["mp3", "mp4"], index=0)
browse = st.button("Browse Directory")
start =  st.button("Start Download",type='primary')
log_placeholder = st.empty()

def download_worker():
    """Handles the download process and logs messages."""
    try:
        download_playlist(format_choice, destination_folder, url, ffmpeg_folder, log_callback=log)
    except Exception as e:
        log(f"Download or postprocessing failed: {str(e)}")
        st.error(e)

if start:
    download_worker()

if browse:
    dirname = filedialog.askdirectory(master=root)
    if dirname:
        destination_folder = dirname
        update_label_area(dirname)
        # Update the placeholder with the new directory
        dir_placeholder.text_input("Enter Destination Folder:", value=dirname)
        st.info(f"Targeted directory : {destination_folder}",icon="📂")
