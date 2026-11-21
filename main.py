"""Core download logic shared by the console and GUI front-ends."""

import os
import re
import subprocess
import sys

from yt_dlp import YoutubeDL

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shared_log.txt")
SUPPORTED_FORMATS = ("mp3", "mp4")

_YOUTUBE_URL_RE = re.compile(
    r"(https?://)?(www\.)?"
    r"(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/playlist\?list=|music\.youtube\.com/playlist\?list=)"
    r"[\w-]+"
)
# Characters that are not allowed in Windows file/folder names.
_INVALID_PATH_CHARS_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
def log_to_file(message):
    """Append a message to the shared log file (read by the log viewer)."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{message}\n")


def log(message):
    """Print a message and append it to the shared log file."""
    print(message)
    log_to_file(message)


def cleanup_log_file():
    """Reset the shared log file, creating it if needed."""
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("Log file empty. Waiting for download to start...\n")


# --------------------------------------------------------------------------- #
# URL helpers
# --------------------------------------------------------------------------- #
def is_valid_youtube_url(url):
    """Quick offline check that the URL looks like a YouTube video/playlist URL."""
    return _YOUTUBE_URL_RE.match(url) is not None


def _extract_info(url):
    """Fetch metadata for a URL without downloading anything."""
    with YoutubeDL({"quiet": True, "extract_flat": "in_playlist", "skip_download": True}) as ydl:
        return ydl.extract_info(url, download=False)


def validate_url_with_yt_dlp(url):
    """Check with yt-dlp that the URL points to something downloadable."""
    try:
        info = _extract_info(url)
        return info is not None and ("entries" in info or "url" in info or "formats" in info)
    except Exception as e:
        log(f"Error validating URL with yt-dlp: {e}")
        return False


def get_playlist_title(url):
    """Return a filesystem-safe title for the playlist (or video)."""
    try:
        title = (_extract_info(url) or {}).get("title")
    except Exception as e:
        log(f"Error extracting playlist metadata: {e}")
        title = None
    title = _INVALID_PATH_CHARS_RE.sub("_", title or "").strip(" .")
    return title or "Unknown Playlist"


# --------------------------------------------------------------------------- #
# Download
# --------------------------------------------------------------------------- #
def prepare_output_dir(destination_folder, playlist_url):
    """Create (if needed) and return the folder the playlist is downloaded into."""
    playlist_directory = os.path.join(destination_folder, get_playlist_title(playlist_url))
    if os.path.isdir(playlist_directory):
        log(f"Target directory: {playlist_directory}")
    else:
        os.makedirs(playlist_directory)
        log(f"Created target directory: {playlist_directory}")
    return playlist_directory


def build_yt_dlp_command(format_choice, output_dir, media_url, ffmpeg_folder=None):
    """Build the yt-dlp command line. yt-dlp handles the mp3/mp4 conversion via ffmpeg."""
    command = [
        sys.executable, "-m", "yt_dlp",
        "--newline",
        "--output", os.path.join(output_dir, "%(title)s.%(ext)s"),
    ]
    if format_choice == "mp3":
        command += ["--format", "bestaudio/best",
                    "--extract-audio", "--audio-format", "mp3", "--audio-quality", "192K"]
    else:
        command += ["--format", "bestvideo+bestaudio/best", "--merge-output-format", "mp4"]
    if ffmpeg_folder:
        command += ["--ffmpeg-location", ffmpeg_folder]
    command.append(media_url)
    return command


def cleanup_dot_part(folder):
    """Delete leftover .part files from an interrupted download."""
    if not folder or not os.path.isdir(folder):
        return
    found = False
    for root, _dirs, files in os.walk(folder):
        for name in files:
            if name.endswith(".part"):
                found = True
                file_path = os.path.join(root, name)
                try:
                    os.remove(file_path)
                    log(f"Deleted temporary file: {file_path}")
                except Exception as e:
                    log(f"Failed to delete {file_path}: {e}")
    if not found:
        log(f"No .part files found in {folder}, nothing to clean up.")


def download_playlist(format_choice, destination_folder, media_url, ffmpeg_folder=None):
    """Download a playlist (or single video) as mp3 or mp4, logging yt-dlp's output.

    Returns True on success, False otherwise.
    """
    if format_choice not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format {format_choice!r}, expected one of {SUPPORTED_FORMATS}")

    cleanup_log_file()
    log("Starting the download process...\n"
        f"    Chosen format: {format_choice}\n"
        f"    Destination folder: {destination_folder}\n"
        f"    Playlist URL: {media_url}")

    playlist_directory = None
    success = False
    try:
        playlist_directory = prepare_output_dir(destination_folder, media_url)
        command = build_yt_dlp_command(format_choice, playlist_directory, media_url, ffmpeg_folder)
        log(f"Running yt-dlp command: {subprocess.list2cmdline(command)}")

        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True, encoding="utf-8", errors="replace", env=env) as process:
            for line in process.stdout:
                line = line.rstrip()
                if line:
                    log(line)

        success = process.returncode == 0
        if success:
            log(f"Successfully downloaded: {media_url}")
        else:
            log(f"yt-dlp exited with code {process.returncode}, see the output above.")
    except Exception as e:
        log(f"Download failed: {e}")
    finally:
        cleanup_dot_part(playlist_directory)
        # Don't leave an empty folder behind if nothing was downloaded.
        if playlist_directory and os.path.isdir(playlist_directory) and not os.listdir(playlist_directory):
            os.rmdir(playlist_directory)
        log("\nTask Completed !")
    return success
