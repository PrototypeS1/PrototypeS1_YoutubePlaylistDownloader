import os
from yt_dlp import YoutubeDL
import regex as re

def is_valid_youtube_url(url):
    # Regular expression pattern for basic YouTube URL validation
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube\.com/watch\?v=|youtu\.be/)'
        '[\w-]+'
    )
    return re.match(youtube_regex, url) is not None

def validate_url_with_yt_dlp(url):
    try:
        with YoutubeDL() as ydl:
            # Attempt to extract info from the URL
            info = ydl.extract_info(url, download=False)
            # Check if the URL points to a valid video or playlist
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

def download_playlist(format_choice, destination_folder, playlist_url):
    def adjust_directory_based_on_playlist(d):
        # This function will be used to modify the output template based on playlist title
        if d['status'] == 'finished':
            # Extract the playlist title and replace 'NA' with 'Download Output'
            playlist_title = d.get('playlist_title', 'NA')
            if playlist_title == 'NA':
                playlist_title = 'Youtube Download Output'
            playlist_directory = os.path.join(destination_folder, playlist_title)
            if not os.path.exists(playlist_directory):
                os.makedirs(playlist_directory)

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
        'progress_hooks': [logger_hook, adjust_directory_based_on_playlist],
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])

def logger_hook(d):
    if d['status'] == 'finished':
        print(f"\nDone downloading video: {d['filename']}")


def validate_user_input(format_choice, playlist_url):
    if not playlist_url:
        print("No valid URL provided. Exiting the program.")
        return False
    if format_choice not in ['mp3', 'mp4']:
        print("You must enter a valid format (either mp3 or mp4).")
        return False
    return True

if __name__ == "__main__":
    format_choice, destination_folder, ffmpeg_folder, playlist_url = get_user_input()
    
    if not validate_user_input(format_choice, playlist_url):
        exit(1)
    
    # Configure ffmpeg path if provided
    configure_ffmpeg(ffmpeg_folder)
    
    # Create destination folder if it doesn't exist
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    download_playlist(format_choice, destination_folder, playlist_url)
