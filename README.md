# YUdl

**English** | [Українська](README.uk.md)

![Version](https://img.shields.io/badge/version-1.0.1-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-3776AB?logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt-6-41CD52?logo=qt&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

**YouTube downloader with a graphical interface.** Python + PyQt6 + yt-dlp.
Paste a link, pick a format, press download — that's it.

Version **1.0.1** · author **msx** · © 2026

## Features

- Simple window: link → Video / Audio → quality or format → progress.
- **Video** — MP4 in Best, 720p or 480p.
- **Audio** — MP3 320 kbps, WAV, FLAC or M4A.
- Progress bar and a **STOP** button.
- Interface languages: **English**, **Русский**, **Українська**.
- Background music toggle.
- FFmpeg is bundled in the `ffmpeg/` folder — no manual setup.
- Built-in update checker for new GitHub releases.
- Download folder is selectable and remembered.

## Requirements

- Windows 10 / 11 (also runs on Linux and macOS)
- Python **3.8+**
- Internet connection

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/RoboLask/YUdl
cd YUdl
```

### 2. Check Python

```bash
python --version
```

If Python is missing, install it from [python.org](https://www.python.org/downloads/)
and tick **Add Python to PATH** during installation.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If `pip` is not found:

```bash
python -m pip install -r requirements.txt
```

### 4. Run

```bash
python main.py
```

On Windows you can also just double-click `main.py`.

On Linux / macOS:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./run.sh
```

## Usage

1. Paste a YouTube link into the **URL** field.
2. Choose **Video** or **Audio**.
3. Pick the quality (Best / 720p / 480p) or the audio format.
4. Select the download folder if needed — the default is your **Downloads**.
5. Press **DOWNLOAD** and wait for the progress bar to finish.

## Formats

| Type | Options | Notes |
|---|---|---|
| Video | Best, 720p, 480p | MP4, merged with FFmpeg |
| Audio | MP3 | 320 kbps, plays everywhere |
| Audio | WAV | uncompressed, large files |
| Audio | FLAC | lossless |
| Audio | M4A | good for iPhone / iTunes |

## Settings

Open **File → Settings**:

- **Background music** — turn the built-in music on or off.
- **Language** — English, Русский or Українська.

Settings are stored in `~/.yudl_settings.json`:

```json
{
  "music": true,
  "output_path": "C:/Users/me/Downloads",
  "language": "en"
}
```

| Field | What it sets | Options |
|---|---|---|
| `music` | background music | `true`, `false` |
| `output_path` | download folder | any folder |
| `language` | interface language | `en`, `ru`, `uk` |

## Project structure

```
main.py           window, download logic and translations
updater.py        update checker for GitHub releases
requirements.txt  Python dependencies
run.sh            Linux / macOS launcher (uses venv)
1.wav             background music
ffmpeg/           bundled FFmpeg binaries
```

## Troubleshooting

**`python` is not recognized**

Python is not in `PATH`. Reinstall it with **Add Python to PATH**, or try:

```bash
py main.py
```

**`pip` is not recognized**

```bash
python -m pip install -r requirements.txt
```

**FFmpeg not found**

Make sure the `ffmpeg/bin/` folder contains `ffmpeg.exe` and `ffprobe.exe`.

**Download seems stuck at 95%**

This is normal — FFmpeg is converting the file. Wait a minute or two.

**Invalid YouTube URL**

Use a link like `https://youtube.com/watch?v=...` or `https://youtu.be/...`.

## Legal

This program is for **personal use only**. Respect YouTube's Terms of Service
and copyright law. You are responsible for what you download.

---

© 2026 msx
