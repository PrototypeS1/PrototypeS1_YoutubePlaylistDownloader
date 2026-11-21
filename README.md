# YouTube Playlist Downloader

Download a whole YouTube playlist (or a single video) as MP3 or MP4, using `yt-dlp` and `ffmpeg`.
It comes with a console app and a Streamlit web GUI with a live log window.

## Features

- Download entire playlists from YouTube.
- **Single title mode**: download just one video, even when its URL is part of a playlist (`watch?v=...&list=...`).
- Choose between MP3 (audio, 192 kbps) and MP4 (video) formats. Default is MP3.
- Playlists go into a sub-folder named after the playlist, inside a destination folder you choose (default is the Desktop). Single titles are saved directly in the destination folder.
- Optionally specify where `ffmpeg` is if it isn't in your system PATH.
- Live log output, in the console or in a separate log window for the GUI.

## Prerequisites

- **Python** >= 3.9
- **ffmpeg**, used by `yt-dlp` to convert audio to MP3 and to merge video and audio into MP4.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/PrototypeS1/PrototypeS1_YoutubePlaylistDownloader.git
cd PrototypeS1_YoutubePlaylistDownloader
```

### 2. Create a virtual environment

**Windows:**

```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS and Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

### 4. Install FFmpeg (if not already done)

Download FFmpeg from [ffmpeg.org](https://www.ffmpeg.org/download.html).
Add its `bin` folder to your system PATH so you don't have to give its location on every download. [Here is a tutorial for Windows](https://phoenixnap.com/kb/ffmpeg-windows).

## Usage

Open a terminal in the cloned repository folder, with the virtual environment activated.

### GUI (web app)

```bash
streamlit run gui.py
```

Your browser should open on the app. If it doesn't, go to <http://localhost:8501>.
Click **Show log** to open a window that follows the download in real time.

### Console

```bash
python console.py
```

You will be prompted for:

1. **Format** (mp3 or mp4): default is mp3.
2. **Mode** (`p` for the whole playlist, `s` for a single title): default is playlist.
3. **Destination folder**: default is the Desktop.
4. **FFmpeg folder**: leave blank if `ffmpeg` is in your PATH.
5. **URL**: the YouTube playlist or video URL.

In the GUI, the same choice is the **Download: Whole playlist / Single title only** option.

How the mode and the URL combine:

| URL | Whole playlist | Single title |
| --- | --- | --- |
| `playlist?list=...` | the playlist | error: no video in the URL |
| `watch?v=...&list=...` | the playlist | only that video |
| `watch?v=...` or `youtu.be/...` | that video | that video |

### Example

- Format: `mp4`
- Mode: `p`
- Destination folder: `C:\Users\Username\Videos`
- FFmpeg folder: `C:\ffmpeg\bin`
- Playlist URL: `https://www.youtube.com/playlist?list=PLxA2cHGHG`

## Project layout

| File | Role |
| --- | --- |
| `main.py` | Core logic: URL validation, building the `yt-dlp` command, logging |
| `console.py` | Interactive console front-end |
| `gui.py` | Streamlit front-end |
| `tkinter_log_viewer.py` | Log window that tails `shared_log.txt` (can also run on its own) |

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp): downloads videos from YouTube and other sites.
- [`ffmpeg`](https://www.ffmpeg.org/): a complete, cross-platform solution to record, convert and stream audio and video.
