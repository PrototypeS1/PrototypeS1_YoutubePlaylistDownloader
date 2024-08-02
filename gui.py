import streamlit as st
import os
import threading
from main import get_user_input, download_playlist, cleanup

# Global variables for cancellation and progress
cancellation_requested = False

def start_download(format_choice, destination_folder, ffmpeg_folder, playlist_url, progress_bar):
    global cancellation_requested
    cancellation_requested = False

    def run_download():
        nonlocal progress_bar
        try:
            # Start downloading
            download_playlist(format_choice, destination_folder, playlist_url, progress_bar)
            st.success("Download completed successfully!")
        except Exception as e:
            st.error(f"An error occurred: {e}")
        finally:
            # Clean up if cancelled
            if cancellation_requested:
                st.warning("Download was cancelled.")
                cleanup(destination_folder)
                progress_bar.empty()
    
    # Run the download in a separate thread
    threading.Thread(target=run_download).start()

def cancel_download():
    global cancellation_requested
    cancellation_requested = True
    st.warning("Cancellation requested. Stopping download...")

# Streamlit UI
st.title("YouTube Playlist Downloader")

# Input fields
format_choice = st.selectbox("Select Format", ["mp3", "mp4"], index=0)
destination_folder = st.text_input("Destination Folder", os.path.join(os.path.expanduser('~'), 'Desktop'))
ffmpeg_folder = st.text_input("FFmpeg Folder (leave blank if not applicable)")
playlist_url = st.text_input("YouTube Playlist/Media URL")

if st.button("Start Download"):
    if not playlist_url:
        st.error("You must enter a valid URL.")
    else:
        # Show progress bar
        progress_bar = st.progress(0)
        start_download(format_choice, destination_folder, ffmpeg_folder, playlist_url, progress_bar)

if st.button("Cancel Download"):
    cancel_download()
