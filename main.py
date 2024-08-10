import os
import threading
import subprocess
import re
from yt_dlp import YoutubeDL

### WIP !! ###############################################################
from pytube import Playlist

def get_playlist_title(playlist_url):
    try:
        playlist = Playlist(playlist_url)
        playlist_title = playlist.title
        return playlist_title if playlist_title else 'Unknown Playlist'
    except Exception as e:
        print(f"Error extracting playlist metadata: {e}")
        return 'Unknown Playlist'
########################################################################

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
        log_to_file(f"Error validating URL with yt-dlp: {e}")
        return False

def configure_ffmpeg(ffmpeg_folder):
    if ffmpeg_folder:
        os.environ['PATH'] += os.pathsep + ffmpeg_folder

def cleanup_dot_part(destination_folder):
    """Clean up .part files in the destination folder."""
    part_files_found = False  # Flag to track if any .part files are found

    if os.path.exists(destination_folder):
        for root, dirs, files in os.walk(destination_folder, topdown=False):
            for name in files:
                if name.endswith('.part'):
                    part_files_found = True  # .part file found
                    file_path = os.path.join(root, name)
                    try:
                        os.remove(file_path)
                        print(f"Deleted temporary file: {file_path}")
                        log_to_file(f"Deleted temporary file: {file_path}")
                    except PermissionError as e:
                        print(f"Permission denied: {file_path}. Error: {e}")
                        log_to_file(f"Permission denied: {file_path}. Error: {e}")
                    except Exception as e:
                        print(f"Failed to delete {file_path}. Error: {e}")
                        log_to_file(f"Failed to delete {file_path}. Error: {e}")

    if not part_files_found:
        print(f"No .part files found in {destination_folder}, cleanup was ignored")
        log_to_file(f"No .part files found in {destination_folder}, cleanup was ignored")


def prepare_output_dir(destination_folder, playlist_url, log_callback):
    """Prepare the output folder for the download and target it."""
    try:
        playlist_directory = os.path.join(destination_folder, get_playlist_title(playlist_url))
        if os.path.exists(playlist_directory):
            print(f"Traget directory: {playlist_directory}")
            if log_callback:
                log_callback(f"Traget directory: {playlist_directory}")
        else:
            os.makedirs(playlist_directory)
            print(f"Created {playlist_directory} directory and targeted it.")
            if log_callback:
                log_callback(f"Created {playlist_directory} directory and targeted it.")
        return playlist_directory
    
    except Exception as e:
        print(f"Error when preparing output folder : {e}")
        if log_callback:
            log_callback(f"Error when preparing output folder : {e}")

def download_playlist(format_choice, destination_folder, playlist_url, log_callback=None):
    """Downloads the entire playlist using yt-dlp via subprocess and logs output."""
    
    print(f"Starting download process for playlist: {playlist_url}")
    cleanup_log_file()
    if log_callback:
        log_callback(f"Starting download process for playlist: {playlist_url}")

    # Prepare output folder
    playlist_directory = prepare_output_dir(destination_folder,playlist_url,log_callback)

    # Prepare yt-dlp command arguments
    ydl_args = [
        'yt-dlp',
        '--format', 'bestaudio/best' if format_choice == 'mp3' else 'bestvideo+bestaudio/best',
        '--output', os.path.join(destination_folder, playlist_directory, '%(title)s.%(ext)s'),
        '--no-playlist' if format_choice == 'mp3' else '',
        playlist_url
    ]

    # Run yt-dlp command
    try:
        print(f"Running yt-dlp command: {' '.join(ydl_args)}")
        if log_callback:
            log_callback(f"Running yt-dlp command: {' '.join(ydl_args)}")
        process = subprocess.Popen(ydl_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Read and log output
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if line:
                print(line)
                if log_callback:
                    log_callback(line)
        
        stderr_output = process.stderr.read()
        if stderr_output:
            print(stderr_output)
            if log_callback:
                log_callback(stderr_output)

        process.wait()
        if process.returncode == 0:
            print(f"Successfully downloaded playlist: {playlist_url}")
            if log_callback:
                log_callback(f"Successfully downloaded playlist: {playlist_url}")
        else:
            print(f"yt-dlp encountered an error: {stderr_output}")
            if log_callback:
                log_callback(f"yt-dlp encountered an error: {stderr_output}")
    except Exception as e:
        print(f"Failed to execute yt-dlp command: {e}")
        if log_callback:
            log_callback(f"Failed to execute yt-dlp command: {e}")
    finally:
        cleanup_dot_part(playlist_directory)
        print("Starting postprocessing...")
        if log_callback:
            log_callback("Starting postprocessing...")
        postprocess_files(playlist_directory)
        print("Postprocessing completed successfully.")
        if log_callback:
            log_callback("Download and postprocessing completed successfully.")

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

def log_to_file(message):
    """Appends a message to a shared log file."""
    log_file = "shared_log.txt"
    with open(log_file, "a") as f:
        f.write(message + "\n")

def cleanup_log_file():
    """Cleans up the shared log file after download process."""
    log_file = "shared_log.txt"
    if os.path.exists(log_file):
        os.remove(log_file)
        print(f"Log file {log_file} deleted successfully.")
    else:
        print(f"Log file {log_file} does not exist, and thus wasn't deleted.")

def postprocess_files(folder, target_format='mp3'):
    """Converts audio and video files to a specified format using ffmpeg."""
    log_to_file("Starting file postprocessing...")
    files_processed = False  # Flag to check if any files are processed
    
    # Supported input formats (could be extended)
    supported_inputs = ['.webm', '.m4a']
    
    for root, dirs, files in os.walk(folder):
        for file in files:
            file_ext = os.path.splitext(file)[1].lower()
            
            if file_ext in supported_inputs:
                files_processed = True  # Set flag when a file is found
                file_path = os.path.join(root, file)
                converted_file = os.path.splitext(file_path)[0] + f'.{target_format}'
                
                try:
                    log_to_file(f"Converting {file_path} to {converted_file}...")
                    
                    # Prepare FFmpeg command
                    command = [
                        "ffmpeg", "-i", file_path, "-vn", "-ar", "44100",
                        "-ac", "2", "-b:a", "192k", converted_file
                    ]
                    
                    # Run FFmpeg command
                    process = subprocess.run(command, capture_output=True, text=True)
                    
                    if process.returncode == 0:
                        os.remove(file_path)  # Remove the original file
                        log_to_file(f"Successfully converted {file_path} to {converted_file}.")
                        print(f"Successfully converted {file_path} to {converted_file}.")
                    else:
                        log_to_file(f"FFmpeg error for {file_path}: {process.stderr}")
                        print(f"FFmpeg error for {file_path}: {process.stderr}")
                
                except Exception as e:
                    log_to_file(f"Conversion failed for {file_path}: {str(e)}")
                    print(f"Conversion failed for {file_path}: {str(e)}")

    if not files_processed:
        log_to_file("No supported files found for postprocessing.")
        print("No supported files found for postprocessing.")
    else:
        log_to_file("Postprocessing completed.")
        print("Postprocessing completed.")