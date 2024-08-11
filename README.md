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
- **ffmpeg** (if you want to convert formats, ie. WebM -> MP3)

## Installation

To set up this project, follow these steps:

### 1. Clone the Repository

Clone the repository to your local machine:

- `git clone https://github.com/PrototypeS1/YoutubePlaylistDownloader.git`
- `cd YoutubePlaylistDownloader`

### 2. Create a Virtual Environment

It’s a good practice to use a virtual environment to manage project dependencies. To create and activate a virtual environment, run the following commands:

**For Windows:**

- `python -m venv venv`
- `venv\Scripts\activate`

**For macOS and Linux:**

- `python3 -m venv venv`
- `source venv/bin/activate`

### 3. Install Dependencies

Once the virtual environment is activated, install the required Python packages:

   `pip install -r requirements.txt`

### 4. Install FFmpeg (if not already done)

If you do not have FFmpeg already installed on your system, you should download it from [here](https://www.ffmpeg.org/download.html).
You should also edit your system environement variables if you want to skip the "Provide FFmpeg location" step each time you perform a download. You can find a tutorial on how to do that [here](https://phoenixnap.com/kb/ffmpeg-windows).

## Usage

**First thing first, open a terminal in the location of the cloned reposirory !**

- ie. in `C:\Users\YouUserName\Documents\RepositoryName` then open a cmd terminal. (on Windows)

### 1. If you want to launch the GUI web application

Run the web-based app with the following command:

- `streamlit run gui.py`

You will be redirected to your browser and can now use the app. If not, launch your browser and follow the link: [to your localhost](http://localhost:8501).
You're all set ! you can now use **Prototype_S1's Youtube Playlist Downloader** freely. See Examples below if you're wondering what to do next.

### 2. If you want to launch the console based application (no GUI)

Run the script with the following command:

- `python console.py`

You will be prompted to enter the following details:

1. **Format** (mp3 or mp4): Default is mp3.
2. **Destination Folder**: Default is the desktop. You can enter the full path to your desired folder.
3. **FFmpeg Folder**: Default is none. If you have `ffmpeg` installed in a custom location, provide the path or press Enter to skip.
4. **Playlist URL**: Provide the URL of the YouTube playlist you want to download.

You're all set ! you can now use **Prototype_S1's Youtube Playlist Downloader** freely. See Examples below if you're wondering what to do next.

## Example

1. **If you want to use the console app**:

   `python console.py`

2. **If you want to use the GUI (Work in Progress, bugs may occur)**:

   `streamlit run gui.py`

- Format (mp3/mp4): mp4
- Destination Folder: C:\Users\Username\Videos
- FFmpeg Folder: C:\ffmpeg
- Playlist URL: <https://www.youtube.com/playlist?list=PLxA2cHGHG>

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- `yt-dlp`: A command-line program to download videos from YouTube and other sites.
- `ffmpeg`: A complete, cross-platform solution to record, convert, and stream audio and video.
- **`pytube`**: A lightweight, Python library for downloading YouTube videos. It simplifies video and playlist downloading with Pythonic interfaces.
