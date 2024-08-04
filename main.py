import os
import re
import threading
from yt_dlp import YoutubeDL
import regex as re
import threading

# Global variables
cancellation_requested = False
download_thread = None

def is_valid_youtube_url(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/playlist\?list=|music\.youtube\.com/playlist\?list=)'
        r'[\w-]+'
    )
    return re.match(youtube_regex, url) is not None

def validate_url_with_yt_dlp(url):
    try:
        with YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)
            return info is not None and ('entries' in info or 'url' in info)
    except Exception as e:
        print(f"Error validating URL with yt-dlp: {e}")
        return False

def get_user_input():
    print("Welcome to YouTube Playlist Downloader.\nYou can leave the program at any time by hitting Ctrl+C\nChoose your options (press enter to set default).")
    
    try:
        format_choice = input("Enter format (mp3/mp4), default is mp3: ").strip().lower() or 'mp3'
        destination_folder = input("Enter destination folder, default is Desktop: ").strip() or os.path.join(os.path.expanduser('~'), 'Desktop')
        ffmpeg_folder = input("Enter path to ffmpeg folder (leave blank if not applicable): ").strip()
        playlist_url = input("Enter the YouTube playlist/media URL: ").strip()
        
        if not playlist_url:
            raise ValueError("You must enter a valid URL")
        if not is_valid_youtube_url(playlist_url) or not validate_url_with_yt_dlp(playlist_url):
            raise ValueError("The provided URL does not appear to be valid for YouTube")
        
        if format_choice not in ['mp3', 'mp4']:
            raise ValueError("You must enter a valid format (either mp3 or mp4)")
        
    except KeyboardInterrupt:
        print("User Keyboard Interrupted. Exiting the program...")
        return None, None, None, None

    except ValueError as e:
        print(e)
        return None, None, None, None
    
    return format_choice, destination_folder, ffmpeg_folder, playlist_url

def configure_ffmpeg(ffmpeg_folder):
    if ffmpeg_folder:
        os.environ['PATH'] += os.pathsep + ffmpeg_folder

def cleanup(destination_folder):
    """Clean up .part files in the destination folder."""
    if os.path.exists(destination_folder):
        for root, dirs, files in os.walk(destination_folder, topdown=False):
            for name in files:
                if name.endswith('.part'):
                    file_path = os.path.join(root, name)
                    try:
                        os.remove(file_path)
                        print(f"Deleted temporary file: {file_path}")
                    except PermissionError as e:
                        print(f"Permission denied: {file_path}. Error: {e}")
                    except Exception as e:
                        print(f"Failed to delete {file_path}. Error: {e}")

def adjust_directory_based_on_playlist(d, destination_folder):
    if d['status'] == 'finished':
        playlist_title = d.get('playlist_title')
        playlist_title = re.sub(r'[\/:*?"<>|]', '', playlist_title)
        playlist_directory = os.path.join(destination_folder, playlist_title)
        playlist_directory = os.path.join(destination_folder, playlist_title)
            
            # Create the directory if it doesn't exist
        playlist_directory = os.path.join(destination_folder, playlist_title)
            
            # Create the directory if it doesn't exist
        if not os.path.exists(playlist_directory):
            os.makedirs(playlist_directory)

def logger_hook(d, destination_folder):
    global cancellation_requested
    if d['status'] == 'finished':
        print(f"\nDone downloading video: {d['filename']}")
    if cancellation_requested:
        print("Download was cancelled.")
        cleanup(destination_folder)
        return

def download_playlist(format_choice, destination_folder, playlist_url, progress_hook=None):
    global cancellation_requested
    ydl_opts = {
        'format': 'bestaudio/best' if format_choice == 'mp3' else 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(destination_folder, '%(playlist_title)s', '%(title)s.%(ext)s'),
        'noplaylist': False,
        'progress_hooks': [lambda d: logger_hook(d, destination_folder), lambda d: adjust_directory_based_on_playlist(d, destination_folder)],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio' if format_choice == 'mp3' else None,
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    if progress_hook:
        ydl_opts['progress_hooks'].append(progress_hook)

    def download_worker():
        global cancellation_requested
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([playlist_url])
        except Exception as e:
            print(f"Download failed: {e}")
        finally:
            if cancellation_requested:
                cleanup(destination_folder)

    cancellation_requested = False
    download_worker()

def validate_user_input(format_choice, playlist_url):
    if not playlist_url:
        print("No valid URL provided. Exiting the program.")
        return False
    if format_choice not in ['mp3', 'mp4']:
        print("You must enter a valid format (either mp3 or mp4).")
        return False
    return True

def start_download(format_choice, destination_folder, ffmpeg_folder, playlist_url):
    configure_ffmpeg(ffmpeg_folder)
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    global download_thread
    download_thread = threading.Thread(
        target=download_playlist, 
        args=(format_choice, destination_folder, playlist_url)
    )
    download_thread.start()

def set_cancellation_requested(requested):
    global cancellation_requested
    cancellation_requested = requested

if __name__ == "__main__":
    format_choice, destination_folder, ffmpeg_folder, playlist_url = get_user_input()
    
    if not validate_user_input(format_choice, playlist_url):
        exit(1)
    
    start_download(format_choice, destination_folder, ffmpeg_folder, playlist_url)
    
    # Wait for the download to finish or handle cancellation
    if download_thread:
        download_thread.join()
