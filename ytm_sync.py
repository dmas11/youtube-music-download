import os
import subprocess
import json
import re
import concurrent.futures
import shutil
import sys
import yt_dlp
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
from rich.console import Console

MUSIC_DIR = os.path.expanduser("~/Music")
# Check for common localized music directories
for local_dir in ["Музыка", "Musique", "Musik", "Musica"]:
    potential = os.path.expanduser(f"~/{local_dir}")
    if os.path.exists(potential):
        MUSIC_DIR = potential
        break

def get_node_path():
    # Try to find node in PATH first
    node_bin = shutil.which("node")
    if node_bin: return node_bin
    
    # Common NVM layout fallback
    nvm_node = os.path.expanduser("~/.nvm/versions/node/v24.14.0/bin/node")
    if os.path.exists(nvm_node): return nvm_node
    
    return "node" # Fallback to just 'node'

NODE_PATH = get_node_path()
YT_DLP = ["python3", "-m", "yt_dlp"]

# Categories that are definitely NOT music
EXCLUDE_CATEGORIES = ["Education", "News & Politics", "Science & Technology", "Movies", "Shows", "Travel & Events"]

# We will now discover these dynamically, but we'll keep a 'fav' list for quick access if needed.
# For now, we'll shift to full discovery.
VERIFIED_MUSIC_PLAYLISTS = [] 

def get_item_category(item):
    """Categorization check - greatly simplified for direct library discovery."""
    return item, "Music" # We trust our direct library scans

def get_library_items():
    print("Discovering library items (playlists and albums)...")
    
    # We use the full library state as a base to avoid 'allat work' of manual URLs
    # This list was discovered via browser scraping for 100% accuracy
    # NOTE: Some browse/MPRE URLs fail to resolve in yt-dlp, so we use direct list IDs where verified.
    PRE_DISCOVERED_ALBUMS = [
        {"title": "Minecraft - Volume Beta", "url": "https://music.youtube.com/playlist?list=OLAK5uy_nnY0s7ogC6wEI85M_C9NrMLLv6lWOQxqY"},
        {"title": "Minecraft - Volume Alpha", "url": "https://music.youtube.com/playlist?list=OLAK5uy_nhQ2EVQRbH-uWJbaesYXRQGZMzinN0qqg"},
        {"title": "Selected Ambient Works 85-92", "url": "https://music.youtube.com/playlist?list=OLAK5uy_npVGHGqWs_-hTzVUivb8lCndQPVB7aIm0"},
        {"title": "Drukqs", "url": "https://music.youtube.com/playlist?list=OLAK5uy_nG46LZ_uffzpRmfuooj3L0LGSJOMBOVQo"},
        {"title": "Syro", "url": "https://music.youtube.com/playlist?list=OLAK5uy_lYw1W8SsabxulshCqGJFlY71VGXedyooc"},
        {"title": "Running From The Internet, Vol. 1 (Original Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_klZxReMOuU562U-e9KldU3DDQsIhnMDxc"},
        {"title": "Terraria (Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_mPd3bgeYqn1kYq4WcMkK81W_Ah0aEQypE"},
        {"title": "Slime Rancher 2, Vol.2 (Original Game Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_m6f3H_Be9d-wgEZ8iexYbTl0Sk_koDAJY"},
        {"title": "Slime Rancher 2 (Original Game Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_lZkvKIZyR18ZHUPdUaiF1pmKRHjr6sovk"},
        {"title": "Slime Rancher (Original Game Soundtrack), Vol. 2", "url": "https://music.youtube.com/playlist?list=OLAK5uy_mbBdg2HkSefEsH2riHFIvBWaMrux0F64A"},
        {"title": "Slime Rancher (Original Game Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_kWMjW9nvHXHjIXgBPfQz3vP4E5jpFuaow"},
        {"title": "Minecraft Dungeons (Original Game Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_lLkMYaC8VvsHDlzqKR1nX-ccJVKBdroWI"},
        {"title": "UNDERTALE Soundtrack", "url": "https://music.youtube.com/playlist?list=OLAK5uy_ljXkQlhVlWyV7BxSxMMzgOLbzYS_-JPt4"},
        {"title": "DELTARUNE Chapter 1 (Original Game Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_kidGzGmzCUSJK1LAtIh7ngZwRF9MT3qjE"},
        {"title": "DELTARUNE Chapters 3+4 (Original Game Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_k-fz2U2mTfcN9R63A7DyL6V_BDUOLpyiE"},
        {"title": "DELTARUNE Chapter 2 (Original Game Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_m-rr6K-H8nfmI3MdSzCRpQw0gxDeG5jzk"},
        {"title": "Selected Ambient Works Volume II", "url": "https://music.youtube.com/playlist?list=OLAK5uy_lOxSWAQX3iFOW6dH_aU_FlFqxFQV42g84"},
        {"title": "The Foundation (Original Game Soundtrack), Vol. 3", "url": "https://music.youtube.com/playlist?list=OLAK5uy_mVMiJRxAH5HCtpSQel-RkiN3AgeYzlo9Y"},
        {"title": "The Foundation (Original Game Soundtrack), Vol. 2", "url": "https://music.youtube.com/playlist?list=OLAK5uy_krzWyMq_JgKyrDh-zjM7ry9oyusXyk0EY"},
        {"title": "Roblox 3008, Vol. 1 (Original Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_ngNQsDqZlbbp5a-BZ6BhQF9VzwY1xDHIQ"},
        {"title": "Minecraft: Nether Update (Original Game Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_lx3LhwbhstxzQcZIXqDBr7sNOjz5ZKr7A"},
        {"title": "Minecraft: Caves & Cliffs (Original Game Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_lY1VUBCMGOEBon7_sJAKPln2oUQvjPR1w"},
        {"title": "Minecraft: The Wild Update (Original Game Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_kZ2SAX1x6Nlf1qj_Z-RHB2he9uXXiuuNs"}
    ]

    def get_playlist_id(url):
        match = re.search(r'list=([a-zA-Z0-9_-]+)', url)
        return match.group(1) if match else url

    # Discovery feeds for playlists (we use multiple to ensure we catch everything)
    targets = [
        "https://www.youtube.com/feed/playlists?view=1", # Created/Saved
        "https://www.youtube.com/feed/playlists",        # All
        "https://www.youtube.com/feed/library"           # Library
    ]
    
    categorized = {"playlists": [], "albums": list(PRE_DISCOVERED_ALBUMS)}
    processed_ids = {get_playlist_id(album["url"]) for album in PRE_DISCOVERED_ALBUMS}

    for target_url in targets:
        cmd = YT_DLP + ["--cookies-from-browser", "firefox", "--flat-playlist", "--dump-json", target_url]
        try:
            cmd += ["--extractor-args", "youtubetab:skip=authcheck"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            for line in res.stdout.splitlines():
                try:
                    data = json.loads(line)
                    title, url = data.get("title"), data.get("url")
                    if not url: continue
                    
                    pid = get_playlist_id(url)
                    if pid in processed_ids: continue
                    
                    # Basic filters for "clean" discovery
                    lower_title = title.lower() if title else ""
                    if any(x in lower_title for x in ["watch later", "history", "liked videos", "сохраненные выпуски", "удаляю интернет"]):
                        continue

                    # If it's a "browse" URL and we haven't processed it, try to resolve it
                    if "/browse/MPRE" in url:
                        # We keep it as is, but we'll try to find its direct playlist ID later if needed
                        pass

                    categorized["playlists"].append({"title": title, "url": url})
                    processed_ids.add(pid)
                except: pass
        except: pass

    # Always include Liked Music
    if "LM" not in processed_ids:
        categorized["playlists"].insert(0, {"title": "Liked music", "url": "https://music.youtube.com/playlist?list=LM"})

    for key in categorized:
        unique = {item["url"]: item for item in categorized[key]}
        categorized[key] = sorted(list(unique.values()), key=lambda x: x["title"].lower() if x["title"] else "")
    
    print(f"Discovery complete. {len(categorized['playlists'])} playlists and {len(categorized['albums'])} albums ready.")
    
    # Persistent cache so it doesn't reset on restart
    try:
        with open(os.path.join(os.getcwd(), "discovery_cache.json"), "w") as f:
            json.dump(categorized, f)
    except: pass
    
    return categorized

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name or "Unnamed")

ALBUMS = [] # Phasing out hardcoded albums

console = Console()

def sync_playlist(name, url, skip_filters=True, prefix="", current_idx=None, total_items=None):
    safe_name = sanitize_filename(name)
    target_dir = os.path.join(MUSIC_DIR, f"{prefix}{safe_name}")
    os.makedirs(target_dir, exist_ok=True)
    
    # Progress Bar Setup
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        # DownloadColumn(), # We'll add this specifically for track task
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
        expand=True
    ) as progress:
        
        # 1. Global/Playlist level task
        playlist_desc = f"Syncing: [bold cyan]{name}[/bold cyan]"
        if current_idx is not None and total_items is not None:
             playlist_desc = f"[{current_idx}/{total_items}] " + playlist_desc
        
        playlist_task = progress.add_task(playlist_desc, total=None)
        
        # Tracker for the current track
        current_track_task = None

        def progress_hook(d):
            nonlocal current_track_task
            if d['status'] == 'downloading':
                if current_track_task is None:
                    filename = os.path.basename(d.get('filename', 'Unknown'))
                    current_track_task = progress.add_task(f"  └─ [yellow]Downloading:[/yellow] {filename}", total=d.get('total_bytes') or d.get('total_bytes_estimate'))
                
                if current_track_task is not None:
                    progress.update(current_track_task, completed=d.get('downloaded_bytes', 0), total=d.get('total_bytes') or d.get('total_bytes_estimate'))
            
            elif d['status'] == 'finished':
                if current_track_task is not None:
                    progress.update(current_track_task, completed=100, total=100, description="  └─ [green]Finished downloading[/green]")
                    progress.remove_task(current_track_task)
                    current_track_task = None
                progress.update(playlist_task, advance=1)

        ydl_opts = {
            'format': 'ba/b',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '0',
            }, {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            }, {
                'key': 'EmbedThumbnail',
            }, {
                'key': 'FFmpegThumbnailsConvertor',
                'format': 'jpg',
            }],
            'outtmpl': f"{target_dir}/%(title)s.%(ext)s",
            'download_archive': os.path.join(target_dir, "archive.txt"),
            'cookiefile': None, # We'll use cookies_from_browser
            'cookiesfrombrowser': ('firefox',),
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'noprogress': True, # We use our own rich progress
            'js_runtimes': {'node': {'binary': NODE_PATH}},
            'extractor_args': {'youtube': {'player_client': ['web', 'android', 'ios']}, 'youtubetab': {'skip': ['authcheck']}},
            'postprocessor_args': {
                'ffmpeg': ['-id3v2_version', '3', '-mapping_family', '0'],
                'ThumbnailsConvertor': ['-qmin', '1', '-qmax', '1']
            },
            'parse_metadata': ["%(album,playlist,playlist_title)s:%(album)s"],
            'progress_hooks': [progress_hook],
        }

        if not skip_filters:
            ydl_opts['match_filter'] = lambda d, *_, **__: None if (d.get('category') == 'Music' or (d.get('artist') and d.get('track') and d.get('album'))) else 'Not Music'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # First, extract info to get the count
            try:
                info = ydl.extract_info(url, download=False)
                if info and 'entries' in info:
                    entries = list(info['entries'])
                    progress.update(playlist_task, total=len(entries))
                    ydl.download([url])
                elif info:
                    progress.update(playlist_task, total=1)
                    ydl.download([url])
                else:
                    console.print(f"[red]Error: Could not retrieve info for {url}[/red]")
            except Exception as e:
                console.print(f"[red]Error starting sync: {e}[/red]")

def print_usage():
    print("""
Usage: sync-music [OPTIONS]

Options:
  -h        Show this help message
  -e        Fast Edit Mode: Jump straight to the local metadata editor
  -m        Fast Manual Mode: Jump straight to manual URL entry
  -s SELECT Sync specific items by index (comma-separated, e.g., -s 1,3,5)
""")

def playlist_sync_menu(cached_playlists=None):
    items = cached_playlists
    if items is None:
        items = get_library_items()["playlists"]
    
    while True:
        print("\n--- Playlists ---")
        for i, item in enumerate(items, 1):
            print(f"[{i}] {item['title'] or '[Private Item]'}")
        
        print("\n[A] Sync ALL")
        print("[S] Re-Scan Library")
        print("[B] Back to Main Menu")
        
        try:
            choice = input("\nSelect numbers (e.g. 1,3) or 'A', 'S', 'B': ").strip().upper()
        except KeyboardInterrupt:
            return items
        if choice == 'B': return items
        if choice == 'S':
            items = get_library_items()["playlists"]
            continue
        
        selected_items = []
        if choice == 'A':
            selected_items = items
        else:
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(',') if x.strip().isdigit()]
                selected_items = [items[i] for i in indices if 0 <= i < len(items)]
            except: pass
            
        if selected_items:
            for i, item in enumerate(selected_items, 1):
                sync_playlist(item["title"] or "Unnamed", item["url"], current_idx=i, total_items=len(selected_items))
    return items

def album_sync_menu(cached_albums=None):
    items = cached_albums
    if items is None:
        items = get_library_items()["albums"]

    while True:
        print("\n--- Albums ---")
        for i, album in enumerate(items, 1):
            print(f"[{i}] {album['title']}")
        
        print("\n[A] Sync ALL")
        print("[S] Re-Scan Library")
        print("[B] Back to Main Menu")
        
        try:
            choice = input("\nSelect index or 'A', 'S', 'B': ").strip().upper()
        except KeyboardInterrupt:
            return items
        if choice == 'B': return items
        if choice == 'S':
            items = get_library_items()["albums"]
            continue
        
        selected_albums = []
        if choice == 'A':
            selected_albums = items
        else:
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(',') if x.strip().isdigit()]
                selected_albums = [items[i] for i in indices if 0 <= i < len(items)]
            except: pass
            
        if selected_albums:
            for i, album in enumerate(selected_albums, 1):
                sync_playlist(album["title"], album["url"], prefix="Album - ", current_idx=i, total_items=len(selected_albums))
    return items

if __name__ == "__main__":
    args = sys.argv[1:]
    
    if "-h" in args:
        print_usage(); sys.exit(0)
    if "-e" in args:
        subprocess.run(["python3", os.path.join(os.getcwd(), "metadata_editor.py")]); sys.exit(0)
    if "-m" in args:
        url = input("URL: "); name = input("Folder Name: ")
        if url and name: sync_playlist(name, url); sys.exit(0)

    # Load persistent cache if available
    cache_file = os.path.join(os.getcwd(), "discovery_cache.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                cached_data = json.load(f)
            # SANITY CHECK: If cache contains old redirects or duplicate Minecraft IDs, force a refresh
            has_old = any("/browse/MPRE" in a.get("url", "") for a in (cached_data.get("albums") or []))
            has_dupes = len(cached_data.get("albums") or []) < 23
            if has_old or has_dupes:
                cached_data = get_library_items()
        except: cached_data = {"playlists": None, "albums": None}
    else:
        cached_data = {"playlists": None, "albums": None}

    try:
        while True:
            print("\n=== YouTube Music Manager ===")
            print("[P] Sync Playlists")
            print("[A] Sync Albums")
            print("[E] Edit Local Metadata")
            print("[M] Manual URL Sync")
            print("[S] Scan Library (Refresh)")
            print("[Q] Quit")
            
            try:
                cmd = input("\nChoice: ").strip().upper()
                if cmd == 'Q': break
                elif cmd == 'E': subprocess.run(["python3", os.path.join(os.getcwd(), "metadata_editor.py")])
                elif cmd == 'A': cached_data["albums"] = album_sync_menu(cached_data["albums"])
                elif cmd == 'P': cached_data["playlists"] = playlist_sync_menu(cached_data["playlists"])
                elif cmd == 'S': 
                    data = get_library_items()
                    cached_data["playlists"], cached_data["albums"] = data["playlists"], data["albums"]
                elif cmd == 'M':
                    url = input("URL: "); name = input("Folder Name: ")
                    if url and name: sync_playlist(name, url)
            except KeyboardInterrupt:
                print("\nExiting...")
                sys.exit(0)
    except KeyboardInterrupt:
        print("\nExiting...")
