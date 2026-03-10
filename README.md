# YTM-Sync: Professional YouTube Music Manager

A robust, interactive command-line tool to synchronize your YouTube Music library to local MP3 files with full metadata, cover art, and a built-in batch editor.

## Features
- **Smart Sync**: Automatically discovers your playlists and saved albums.
- **Deep Filtering**: Excludes non-music content and "ghost" playlists using content analysis.
- **Rich Metadata**: Automatically embeds high-quality cover art (JPG), Artist, Album, and Year tags.
- **Smart Fallback**: Tracks without album tags automatically inherit the playlist name.
- **Interactive TUI**: Easy-to-use menus for selecting specific items or syncing your whole library.
- **Batch Metadata Editor**: Built-in tool to manually refine your local music tags.
- **High Performance**: Parallel processing for fast library scanning.

## Installation

### 1. Prerequisites
- **Python 3.8+**
- **FFmpeg**: Required for audio conversion and metadata embedding.
- **yt-dlp**: Automated music downloader.
- **Node.js**: Recommended for solving YouTube's signature challenges.

### 2. Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/dmas11/youtube-music-download.git
   cd youtube-music-download
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. **Authentication**: This tool requires cookies from a logged-in browser (Firefox by default) to access your private playlists and albums. Ensure you are logged into YouTube/YT Music in Firefox.

## Usage

Simply run the sync script:
```bash
./sync.sh
```

### Advanced Flags
- `-h`: Show help and all available flags.
- `-e`: Launch only the **Metadata Editor** (skip discovery).
- `-m`: Launch only **Manual Mode** for direct URL syncing.
- `-s <indices>`: Automatically select specific items (e.g., `./sync.sh -s 1,5`).

## Configuration
By default, the tool looks for a folder named `Music` or `Музыка` in your home directory. You can modify the `MUSIC_DIR` variable in `ytm_sync.py` if you use a different path.

## License
MIT
