import os
from yt_dlp import YoutubeDL


def get_user_input():
    print("Welcome to YouTube Playlist Downloader.\nChoose your options (press enter to set default).")
    
    format_choice = input("Enter format (mp3/mp4), default is mp3: ").strip().lower() or 'mp3'
    destination_folder = input("Enter destination folder, default is Desktop: ").strip() or os.path.join(os.path.expanduser('~'), 'Desktop')
    ffmpeg_folder = input("Enter path to ffmpeg folder (leave blank if not applicable): ").strip()
    playlist_url = input("Enter the YouTube playlist URL: ").strip()
    
    return format_choice, destination_folder, ffmpeg_folder, playlist_url

def configure_ffmpeg(ffmpeg_folder):
    if ffmpeg_folder:
        os.environ['PATH'] += os.pathsep + ffmpeg_folder

def download_playlist(format_choice, destination_folder, playlist_url):
    # Setup yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best' if format_choice == 'mp3' else 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(destination_folder, '%(playlist_title)s', '%(title)s.%(ext)s'),
        'noplaylist': False,
        'progress_hooks': [logger_hook],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio' if format_choice == 'mp3' else None,
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])

def logger_hook(d):
    if d['status'] == 'finished':
        print(f"\nDone downloading video: {d['filename']}")

if __name__ == "__main__":
    format_choice, destination_folder, ffmpeg_folder, playlist_url = get_user_input()
    
    # Configure ffmpeg path if provided
    configure_ffmpeg(ffmpeg_folder)
    
    # Create destination folder if it doesn't exist
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    download_playlist(format_choice, destination_folder, playlist_url)
