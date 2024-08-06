import os
from main import configure_ffmpeg, download_playlist, validate_url_with_yt_dlp, is_valid_youtube_url, cleanup

def get_user_input():
    """Get user input from the console."""
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

if __name__ == "__main__":
    format_choice, destination_folder, ffmpeg_folder, playlist_url = get_user_input()
    
    if format_choice and destination_folder and ffmpeg_folder and playlist_url:
        configure_ffmpeg(ffmpeg_folder)
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        download_playlist(format_choice, destination_folder, playlist_url)