"""Core download logic shared by the console and GUI front-ends."""

import os
import re
import subprocess
import sys
from datetime import date
from urllib.parse import parse_qs, urlparse

from yt_dlp import YoutubeDL
from yt_dlp.version import __version__ as YT_DLP_VERSION

# YouTube changes often; yt-dlp releases older than this usually stop working.
YT_DLP_MAX_AGE_DAYS = 90

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shared_log.txt")
SUPPORTED_FORMATS = ("mp3", "mp4")

_YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"}
_YOUTUBE_ID_RE = re.compile(r"[\w-]+")
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
def _parse(url):
    if "://" not in url:
        url = "https://" + url
    return urlparse(url.strip())


def parse_youtube_url(url):
    """Return (video_id, playlist_id) from a YouTube URL; either may be None.

    Handles youtube.com, www./m./music.youtube.com, youtu.be and /shorts/ links, e.g.
    ``watch?v=abc&list=PLx`` -> ("abc", "PLx"), ``playlist?list=PLx`` -> (None, "PLx").
    """
    parsed = _parse(url)
    host = (parsed.hostname or "").lower()
    query = parse_qs(parsed.query)
    path_parts = [p for p in parsed.path.split("/") if p]

    video_id = query.get("v", [None])[0]
    if host == "youtu.be" and path_parts:
        video_id = path_parts[0]
    elif len(path_parts) >= 2 and path_parts[0] in ("shorts", "live", "embed"):
        video_id = path_parts[1]
    playlist_id = query.get("list", [None])[0]

    def clean(value):
        return value if value and _YOUTUBE_ID_RE.fullmatch(value) else None

    return clean(video_id), clean(playlist_id)


def is_valid_youtube_url(url):
    """Quick offline check: a YouTube (or YouTube Music) URL with a video or playlist in it."""
    host = (_parse(url).hostname or "").lower()
    return host in _YOUTUBE_HOSTS and any(parse_youtube_url(url))


def _extract_info(url, single=False):
    """Fetch metadata for a URL without downloading anything."""
    options = {"quiet": True, "extract_flat": "in_playlist", "skip_download": True,
               "noplaylist": single}
    with YoutubeDL(options) as ydl:
        return ydl.extract_info(url, download=False)


def validate_url_with_yt_dlp(url, single=False):
    """Check with yt-dlp that the URL points to something downloadable."""
    try:
        info = _extract_info(url, single)
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


def build_yt_dlp_command(format_choice, output_dir, media_url, ffmpeg_folder=None, single=False):
    """Build the yt-dlp command line. yt-dlp handles the mp3/mp4 conversion via ffmpeg.

    With single=True only the video is downloaded, even if the URL also points to a playlist.
    """
    command = [
        sys.executable, "-m", "yt_dlp",
        "--newline",
        "--no-playlist" if single else "--yes-playlist",
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


def yt_dlp_age_days(version=YT_DLP_VERSION, today=None):
    """Age in days of a yt-dlp version like '2025.09.05', or None if it can't be parsed."""
    try:
        year, month, day = (int(part) for part in version.split(".")[:3])
        return ((today or date.today()) - date(year, month, day)).days
    except (ValueError, TypeError):
        return None


def failure_hints(output_lines, version=YT_DLP_VERSION, today=None):
    """Return human-readable hints explaining a failed download, based on yt-dlp's output."""
    hints = []
    age = yt_dlp_age_days(version, today)
    if age is not None and age > YT_DLP_MAX_AGE_DAYS:
        hints.append(
            f"Your yt-dlp ({version}) is {age} days old, and YouTube regularly breaks old versions. "
            f"Update it with:\n    \"{sys.executable}\" -m pip install -U yt-dlp")
    # yt-dlp warns about a missing JS runtime on every run, so only point at it
    # when signature extraction (which needs that runtime) actually failed.
    if any("Signature extraction failed" in line for line in output_lines):
        hints.append("yt-dlp needs a JavaScript runtime for YouTube. Installing deno "
                     "(https://deno.com, e.g. `winget install DenoLand.Deno`) usually fixes this.")
    return hints


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


def resolve_single_mode(media_url, single):
    """Decide whether to download a single title, given the URL and the requested mode.

    Raises ValueError when a single title is requested but the URL has no video in it.
    """
    video_id, playlist_id = parse_youtube_url(media_url)
    if single and not video_id:
        raise ValueError("Single title mode needs a video URL (watch?v=... or youtu.be/...), "
                         "not a playlist-only URL.")
    if not single and not playlist_id:
        log("The URL has no playlist in it, downloading it as a single title.")
        return True
    return single


def download_playlist(format_choice, destination_folder, media_url, ffmpeg_folder=None, single=False):
    """Download a playlist, or a single title with single=True, as mp3 or mp4.

    Playlists go into a sub-folder named after the playlist; single titles go
    straight into destination_folder. Returns True on success, False otherwise.
    """
    if format_choice not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format {format_choice!r}, expected one of {SUPPORTED_FORMATS}")

    cleanup_log_file()
    log("Starting the download process...\n"
        f"    Mode: {'single title' if single else 'playlist'}\n"
        f"    Chosen format: {format_choice}\n"
        f"    Destination folder: {destination_folder}\n"
        f"    URL: {media_url}")

    playlist_directory = None
    success = False
    try:
        single = resolve_single_mode(media_url, single)
        if single:
            output_dir = destination_folder
        else:
            output_dir = playlist_directory = prepare_output_dir(destination_folder, media_url)
        command = build_yt_dlp_command(format_choice, output_dir, media_url, ffmpeg_folder, single)
        log(f"Running yt-dlp command: {subprocess.list2cmdline(command)}")

        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        output_lines = []
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True, encoding="utf-8", errors="replace", env=env) as process:
            for line in process.stdout:
                line = line.rstrip()
                if line:
                    log(line)
                    output_lines.append(line)

        success = process.returncode == 0
        if success:
            log(f"Successfully downloaded: {media_url}")
        else:
            log(f"yt-dlp exited with code {process.returncode}, see the output above.")
            for hint in failure_hints(output_lines):
                log(f"Hint: {hint}")
    except Exception as e:
        log(f"Download failed: {e}")
    finally:
        # Only clean the playlist sub-folder: in single mode we never touch the
        # rest of the user's destination folder.
        cleanup_dot_part(playlist_directory)
        # Don't leave an empty folder behind if nothing was downloaded.
        if playlist_directory and os.path.isdir(playlist_directory) and not os.listdir(playlist_directory):
            os.rmdir(playlist_directory)
        log("\nTask Completed !")
    return success
