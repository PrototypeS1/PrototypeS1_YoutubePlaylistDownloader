"""Streamlit front-end. Run with: streamlit run gui.py"""

import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog

import streamlit as st

from main import (SUPPORTED_FORMATS, cleanup_log_file, download_playlist,
                  is_valid_youtube_url, parse_youtube_url)

LOG_VIEWER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tkinter_log_viewer.py")

if "destination_folder" not in st.session_state:
    st.session_state["destination_folder"] = os.path.join(os.path.expanduser("~"), "Desktop")
    cleanup_log_file()


def browse_directory():
    """Open a native folder picker and store the result in the destination field."""
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", 1)
    try:
        dirname = filedialog.askdirectory(master=root)
    finally:
        root.destroy()
    if dirname:
        st.session_state["destination_folder"] = dirname


def open_log_viewer():
    """Launch the log viewer in its own process so it doesn't block Streamlit."""
    subprocess.Popen([sys.executable, LOG_VIEWER])


st.title("YouTube Playlist Downloader", help="Brought to you by Prototype_S1")

url = st.text_input("Enter Playlist or Video URL:").strip()
mode = st.radio("Download", ["Whole playlist", "Single title only"], horizontal=True,
                help="'Single title only' downloads just the video in the URL, even if it is "
                     "part of a playlist, and saves it directly in the destination folder.")
single = mode == "Single title only"
destination_folder = st.text_input("Enter Destination Folder:", key="destination_folder")
ffmpeg_folder = st.text_input(
    "Enter FFmpeg Folder (optional, leave blank if set up in the system PATH):").strip()
format_choice = st.selectbox("Choose Format", SUPPORTED_FORMATS, index=0)

st.button("Browse Directory", on_click=browse_directory)
st.button("Show log", on_click=open_log_viewer)
start = st.button("Start Download", type="primary")

if start:
    if not is_valid_youtube_url(url):
        st.error("Please enter a valid YouTube playlist or video URL.")
    elif single and not parse_youtube_url(url)[0]:
        st.error("'Single title only' needs a video URL (watch?v=... or youtu.be/...), "
                 "not a playlist-only URL.")
    else:
        os.makedirs(destination_folder, exist_ok=True)
        with st.spinner("Downloading... click 'Show log' to follow progress."):
            ok = download_playlist(format_choice, destination_folder, url, ffmpeg_folder or None, single)
        if ok:
            st.success(f"Download finished in {destination_folder}", icon="📂")
        else:
            st.error("Download failed, open the log for details.")
