# YouTube Playlist Downloader

This Python script downloads a playlist from YouTube using `yt-dlp` and `ffmpeg`. The script supports downloading in MP3 or MP4 formats and allows users to specify the destination folder and `ffmpeg` path.

## Features

- Download entire playlists from YouTube.
- Choose between MP3 and MP4 formats (default is MP3).
- Specify destination folder (default is the desktop).
- Optionally specify the path to `ffmpeg` (default is none).
- Provides log feedback using `yt-dlp` logger.

## Prerequisites

Ensure you have the following installed:

- **Python** (>= 3.6)
- **yt-dlp** (Python package)
- **ffmpeg** (if downloading MP4 or if you want to convert formats)

## Installation

1. **Install dependencies:**
   - It is recommended to create a virtual environement before installing modules.
   - `pip install -r requirements.txt`


2. **Install `ffmpeg`:**

   - Download and install `ffmpeg` from [ffmpeg.org](https://ffmpeg.org/download.html).
   - Ensure `ffmpeg` is in your system's PATH or provide its path when prompted.

## Usage

Run the script with the following command:

   `python main.py`

You will be prompted to enter the following details:

1. **Format** (mp3 or mp4): Default is mp3.
2. **Destination Folder**: Default is the desktop. You can enter the full path to your desired folder.
3. **FFmpeg Folder**: Default is none. If you have `ffmpeg` installed in a custom location, provide the path or press Enter to skip.
4. **Playlist URL**: Provide the URL of the YouTube playlist you want to download.

## Example

   `python main.py`

   - Format (mp3/mp4): mp4
   - Destination Folder: C:\Users\Username\Videos
   - FFmpeg Folder: C:\ffmpeg
   - Playlist URL: https://www.youtube.com/playlist?list=PLxA2cHGHG

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- `yt-dlp`: A command-line program to download videos from YouTube and other sites.
- `ffmpeg`: A complete, cross-platform solution to record, convert, and stream audio and video.
