"""Interactive console front-end. Run with: python console.py"""

import os

from main import (SUPPORTED_FORMATS, download_playlist, is_valid_youtube_url,
                  parse_youtube_url, validate_url_with_yt_dlp)


def get_user_input():
    """Ask the user for the download options. Returns None if cancelled or invalid."""
    print("Welcome to YouTube Playlist Downloader.\n"
          "You can leave the program at any time by hitting Ctrl+C\n"
          "Choose your options (press Enter to keep the default).")
    try:
        format_choice = input("Enter format (mp3/mp4), default is mp3: ").strip().lower() or "mp3"
        if format_choice not in SUPPORTED_FORMATS:
            raise ValueError("You must enter a valid format (either mp3 or mp4)")
        print(f"You chose {format_choice}.")

        mode = input("Download the whole (p)laylist or a (s)ingle title? default is playlist: ").strip().lower() or "p"
        if mode not in ("p", "playlist", "s", "single"):
            raise ValueError("You must enter a valid mode (p for playlist or s for single title)")
        single = mode.startswith("s")
        print(f"You chose {'a single title' if single else 'the whole playlist'}.")

        default_folder = os.path.join(os.path.expanduser("~"), "Desktop")
        destination_folder = input("Enter destination folder, default is Desktop: ").strip() or default_folder
        print(f"You chose {destination_folder}.")

        ffmpeg_folder = input("Enter path to ffmpeg folder (leave blank if not applicable): ").strip()
        if ffmpeg_folder:
            print(f"You chose {ffmpeg_folder} as ffmpeg folder path.")
        else:
            print("No custom ffmpeg folder given, ffmpeg must be in your system PATH.")

        playlist_url = input("Enter the YouTube playlist/media URL: ").strip()
        if not playlist_url:
            raise ValueError("You must enter a valid URL")
        if not is_valid_youtube_url(playlist_url) or not validate_url_with_yt_dlp(playlist_url, single):
            raise ValueError("The provided URL does not appear to be valid for YouTube")
        video_id, _playlist_id = parse_youtube_url(playlist_url)
        if single and not video_id:
            raise ValueError("Single title mode needs a video URL (watch?v=... or youtu.be/...), "
                             "not a playlist-only URL")
        print(f"You chose {playlist_url} as the targeted URL.")
    except KeyboardInterrupt:
        print("\nUser Keyboard Interrupted. Exiting the program...")
        return None
    except ValueError as e:
        print(e)
        return None

    return format_choice, destination_folder, ffmpeg_folder or None, playlist_url, single


def main():
    options = get_user_input()
    if options is None:
        return
    format_choice, destination_folder, ffmpeg_folder, playlist_url, single = options
    download_playlist(format_choice, destination_folder, playlist_url, ffmpeg_folder, single)


if __name__ == "__main__":
    main()
