import os
from main import configure_ffmpeg, download_playlist, validate_url_with_yt_dlp, is_valid_youtube_url, postprocess_files

def get_user_input():
    """Get user input from the console."""
    print("Welcome to YouTube Playlist Downloader.\nYou can leave the program at any time by hitting Ctrl+C\nChoose your options (press enter to set default).")
    
    try:
        format_choice = input("Enter format (mp3/mp4), default is mp3: ").strip().lower() or 'mp3'
        print(f"You chose {format_choice}.")
        destination_folder = input("Enter destination folder, default is Desktop: ").strip() or os.path.join(os.path.expanduser('~'), 'Desktop')
        print(f"You chose {destination_folder}.")
        ffmpeg_folder = input("Enter path to ffmpeg folder (leave blank if not applicable): ").strip()
        if ffmpeg_folder == "":
            print("You ignored the custom FFMPEG folder path, you must have installed FFMPEG in your system PATH")
        else:
            print(f"You chose {ffmpeg_folder} as ffmpeg folder path.")
        playlist_url = input("Enter the YouTube playlist/media URL: ").strip()
        print(f"You chose {playlist_url} as the targeted playlist url.")
        
        if not playlist_url:
            raise ValueError("You must enter a valid URL")
        if not is_valid_youtube_url(playlist_url) or not validate_url_with_yt_dlp(playlist_url):
            raise ValueError("The provided URL does not appear to be valid for YouTube")
        
        if format_choice not in ['mp3', 'mp4']:
            raise ValueError("You must enter a valid format (either mp3 or mp4)")
        
    except KeyboardInterrupt:
        print("\nUser Keyboard Interrupted. Exiting the program...")
        return None, None, None, None

    except ValueError as e:
        print(e)
        return None, None, None, None
    
    return format_choice, destination_folder, ffmpeg_folder, playlist_url

def main():
    format_choice, destination_folder, ffmpeg_folder, playlist_url = get_user_input()
    
    if format_choice and destination_folder and playlist_url:
        # Configure FFmpeg
        if ffmpeg_folder:
            print(f"Configuring FFmpeg with folder: {ffmpeg_folder}")
            configure_ffmpeg(ffmpeg_folder)
        
        # Create destination folder if it does not exist
        if not os.path.exists(destination_folder):
            print(f"Creating destination folder: {destination_folder}")
            os.makedirs(destination_folder)
        
        # Start the download process
        print(f"Starting download to {destination_folder}...")
        try:
            download_playlist(format_choice, destination_folder, playlist_url)
            print("Download completed successfully.")
            
            # Check for downloaded files
            files = [os.path.join(root, file) for root, dirs, files in os.walk(destination_folder) for file in files]
            if not files:
                print(f"No files found in destination folder: {destination_folder}")
            else:
                print(f"Files found in destination folder: {files}")
                
            # Post-process files if the format is mp3
            if format_choice == 'mp3':
                try:
                    print("Starting post-processing...")
                    postprocess_files(destination_folder)
                    print("Post-processing completed.")
                except Exception as e:
                    print(f"Post-processing failed with error: {e}")

        except Exception as e:
            print(f"Download failed with error: {e}")

if __name__ == "__main__":
    main()
