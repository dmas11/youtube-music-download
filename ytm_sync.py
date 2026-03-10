import os
import subprocess
import json
import re
import concurrent.futures
import shutil

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

VERIFIED_MUSIC_PLAYLISTS = [
  {"title": "Понравившаяся музыка", "url": "https://music.youtube.com/playlist?list=LM"},
  {"title": "TikTok Songs", "url": "https://music.youtube.com/playlist?list=PLHrM7HbaQ1Ahdj_oKGfLDT90mJZ-Keq_Q"},
  {"title": "Grace OST", "url": "https://music.youtube.com/playlist?list=PLRkjGcL9HL6CbBuvvnlntngEh_83ZnOLt"},
  {"title": "Ultracore", "url": "https://music.youtube.com/playlist?list=PLHrM7HbaQ1Aib5UiMZsD4mQDCV9kn_GdF"},
  {"title": "Smash hit OST [in order of Checkpoints]", "url": "https://music.youtube.com/playlist?list=PLR8-BKNj8vBd3H_ktQ-P3oz1l9WbWcqlF"},
  {"title": "sv", "url": "https://music.youtube.com/playlist?list=PLHrM7HbaQ1AjyJ36qkmRLqH1-1letwTW4"},
  {"title": "Vocaloid", "url": "https://music.youtube.com/playlist?list=PLHrM7HbaQ1Ahp7RBJhhdDsQYvWTt58gng"},
  {"title": "Areo", "url": "https://music.youtube.com/playlist?list=PLHrM7HbaQ1Ag2O_qykf1ix3ETeR9uBCPD"},
  {"title": "sr", "url": "https://music.youtube.com/playlist?list=PLHrM7HbaQ1AjncjuMdCZf3yWzduRoKEot"},
  {"title": "Heyselcuk Ai Synthwave Music", "url": "https://music.youtube.com/playlist?list=PLqijHsE8ioug3ToAyDXd4Z7BPnKoFIETm"},
  {"title": "2025 Recap", "url": "https://music.youtube.com/playlist?list=LRYR7ZRZTOkqGWK-Z7UTHoH8xgFNPCmyeFnXF"},
  {"title": "Combat Initiation", "url": "https://music.youtube.com/playlist?list=PLS1Fje5-SsBrn5rcjlPVE3aCAtlLqJhTY"},
  {"title": "Silksong OST", "url": "https://music.youtube.com/playlist?list=PLfUKr9nPvx8ABgIm4YYOcY0fLz-za7jA7"},
  {"title": "C418 - Minecraft: Volume Final (Confirmed / speculated songs)", "url": "https://music.youtube.com/playlist?list=PL7i1I9QFAv7OWMgbXwCz66UB8xbOOxGq7"},
  {"title": "The Complete ULTRAKILL OST", "url": "https://music.youtube.com/playlist?list=PL_7N2OGhRlMf2Hi3eDKvJlW9IUV366oT3"},
  {"title": "Work breakcore", "url": "https://music.youtube.com/playlist?list=PLOMPw_qbdnq1UlctJ-Fk-O5QbNMgmukau"},
  {"title": "Something Evil Will Happen OST", "url": "https://music.youtube.com/playlist?list=PLO7Lc9CGFoJP8j41mWKSn2g5pKlRCnBc1"},
  {"title": "ROBLOX Music", "url": "https://music.youtube.com/playlist?list=PLmJLiAlf24OjDLmlQ66DRWj_RqpRYW7Xd"},
  {"title": "Forsaken OST (Roblox)", "url": "https://music.youtube.com/playlist?list=PLAl67ptS1aswzAivpHhYc7b66_w2JrtDd"},
  {"title": "Hollow Knight Ambience 10h", "url": "https://music.youtube.com/playlist?list=PLfUKr9nPvx8Cey-mKoaC4QpGTfM2nO7Xm"},
  {"title": "OneShot Full OST", "url": "https://music.youtube.com/playlist?list=PLa73G0dLHZJC2PQWXSLAbmoCA8sj0IdeM"},
  {"title": "SWAPPERTALE (beats 2 and 4 are swapped)", "url": "https://music.youtube.com/playlist?list=PL7WohJN28CH6sP1RGNadOuRkJL2d-N_ru"},
  {"title": "PRESSURE OFFICIAL GAME OST", "url": "https://music.youtube.com/playlist?list=PL0up-UAK8KPWcAjVTHL6NMU1wZChMdYRo"},
  {"title": "DOORS Roblox OST", "url": "https://music.youtube.com/playlist?list=PLR7tH5RWHYe6O-wx-PJmVk5K1boGTJTuc"},
  {"title": "🍄Dreamcore/Weirdcore👁", "url": "https://music.youtube.com/playlist?list=PLF_WTWH2u3I9HFWY-xibGoiCrvgvqgXHF"},
  {"title": "Baba Is You OST", "url": "https://music.youtube.com/playlist?list=PLMoZgWjm14OF2AWFfPc3cyQH7T2SC89jo"},
  {"title": "Minecraft Soundtrack", "url": "https://music.youtube.com/playlist?list=PLP_-9d7m0d3e61gxuu5g1rcNCa7L8ObaH"},
  {"title": "Portal Songs + Films", "url": "https://music.youtube.com/playlist?list=PLECBCD09F7DAFDA8C"},
  {"title": "Minecraft Volume Alpha", "url": "https://music.youtube.com/playlist?list=PLHykAyQQdTart3T8wrDjEnAFEmbVstInA"},
  {"title": "Impossible Piano Tutorials from Sheet Music Boss", "url": "https://music.youtube.com/playlist?list=PLDvkGjpaMAmzc5IDm8vVRbFBtYJZHs0Mx"},
  {"title": "Human Fall Flat Full OST", "url": "https://music.youtube.com/playlist?list=PLIjPUgWn2kINgbcEkMv6HlZ2u9qhRfdAz"},
  {"title": "msk", "url": "https://music.youtube.com/playlist?list=PLHrM7HbaQ1AhYUY_qGGjhCp1oonUnAqee"},
  {"title": "NCS", "url": "https://music.youtube.com/playlist?list=PLHrM7HbaQ1AjqI06osps58LJsR58POJE1"},
  {"title": "Superliminal OST (Official)", "url": "https://music.youtube.com/playlist?list=PL4l-_roC68Gwmt668QBow23JKyOPwrBb8"},
  {"title": "Superliminal OST", "url": "https://music.youtube.com/playlist?list=PL4l-_roC68GzrmReXuez9Nt7_EGLvD0rm"},
  {"title": "Hollow Knight Voice", "url": "https://music.youtube.com/playlist?list=PLXSGzFtDdC39q6UgcpWElC9ho66ZBqpSr"},
  {"title": "Hollow Knight: Gods & Nightmares", "url": "https://music.youtube.com/playlist?list=PLYnSM_n8EAqzP1Asp99QQHPdzA6wlZYrh"},
  {"title": "Hollow Knight: The Grimm Troupe", "url": "https://music.youtube.com/playlist?list=PLYnSM_n8EAqw1ATaEGvLclOwciuCg8EMB"},
  {"title": "Hollow Knight: Hidden Dreams", "url": "https://music.youtube.com/playlist?list=PLYnSM_n8EAqzxXH0swyCcvwoHBGgUGF70"},
  {"title": "Soundtrack Sunday", "url": "https://music.youtube.com/playlist?list=PLYnSM_n8EAqz1FyXeQDxhqDXbJ0dGbS2Y"},
  {"title": "Cats are Liquid - A Better Place - OST", "url": "https://music.youtube.com/playlist?list=PLaf72QlWgB6ed4_U-jCt43w6IjIjGdyGr"}
]

def get_item_category(item):
    """Checks the category of the first few items in a playlist."""
    url = item.get("url")
    title = item.get("title", "").lower()
    
    # Priority keywords for music-related content (stricter)
    # If these are in the title, we trust it more.
    trust_score = 0
    if any(k in title for k in ["album", "ost", "soundtrack", "remix", "breakcore", "synthwave", "chill", "lofi", "ambient", "radio"]):
        trust_score += 2
    if any(k in title for k in ["music", "song"]):
        trust_score += 1
        
    try:
        # Check first 3 items
        cmd = YT_DLP + ["--cookies-from-browser", "firefox", "--print", "category", "--playlist-items", "1-3", url]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        categories = [c.strip() for c in res.stdout.splitlines() if c.strip()]
        
        # If any of the first 3 are Music, it's a win
        if "Music" in categories:
            return item, "Music"
            
        # If all items are in exclude list, it's a definite NO
        if categories and all(c in EXCLUDE_CATEGORIES or c == "Gaming" for c in categories):
            # Exception: if trust score is high, it might be an OST categorized as Gaming
            if trust_score >= 2:
                return item, "Music"
            return item, "Exclude"
            
        # Default fallback for ambiguous ones
        if trust_score >= 1:
            return item, "Music"
            
        return item, "Exclude"
    except:
        # On timeout/error, we default to Exclude to be safe, unless trust score is high
        if trust_score >= 2:
            return item, "Music"
        return item, "Exclude"

def get_library_items():
    print("Discovering library items (playlists and albums)...")
    
    items_by_id = {} # Key: Playlist ID, Value: item
    
    def get_playlist_id(url):
        match = re.search(r'list=([a-zA-Z0-9_-]+)', url)
        return match.group(1) if match else url

    # Add verified ones first
    for item in VERIFIED_MUSIC_PLAYLISTS:
        pid = get_playlist_id(item["url"])
        if pid not in items_by_id:
            items_by_id[pid] = item
    
    # Broad targets for new discovery, but we rely on strict filtering below
    targets = [
        "https://www.youtube.com/feed/playlists",      # All playlists
        "https://www.youtube.com/feed/playlists?view=1", # Only created playlists
        "https://www.youtube.com/feed/library"         # General library
    ]
    
    discovered_count = 0
    for target in targets:
        cmd = YT_DLP + ["--cookies-from-browser", "firefox", "--flat-playlist", "--dump-json", target]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            for line in res.stdout.splitlines():
                try:
                    data = json.loads(line)
                    title, url = data.get("title"), data.get("url")
                    if url:
                        pid = get_playlist_id(url)
                        if pid not in items_by_id:
                            # Stricter exclusion: hide known system/non-music titles
                            lower_title = title.lower() if title else ""
                            if not any(x in lower_title for x in ["watch later", "history", "liked videos", "сохраненные выпуски", "сохр1", "сохр2", "удаляю интернет"]):
                                items_by_id[pid] = {"title": title, "url": url}
                                discovered_count += 1
                except: pass
        except: pass

    if not items_by_id: return []

    print(f"Discovered {len(items_by_id)} unique library items ({discovered_count} new). Refining list by content...")
    music_items = []
    
    # Verified ones are skipped from the expensive category check
    verified_ids = {get_playlist_id(item["url"]) for item in VERIFIED_MUSIC_PLAYLISTS}
    
    def check_and_filter(pid, item):
        if pid in verified_ids:
            return item, "Music"
        return get_item_category(item)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_id = {executor.submit(check_and_filter, pid, item): pid for pid, item in items_by_id.items()}
        for future in concurrent.futures.as_completed(future_to_id):
            try:
                item, category = future.result()
                if category == "Music":
                    music_items.append(item)
            except: pass

    music_items.sort(key=lambda x: x["title"].lower() if x["title"] else "")
    print(f"Discovery complete. {len(music_items)} items ready.")
    return music_items

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name or "Unnamed")

ALBUMS = [
  {"title": "Minecraft: Caves & Cliffs (Original Game Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_lY1VUBCMGOEBon7_sJAKPln2oUQvjPR1w"},
  {"title": "The Foundation (Original Game Soundtrack), Vol. 3", "url": "https://music.youtube.com/playlist?list=OLAK5uy_mVMiJRxAH5HCtpSQel-RkiN3AgeYzlo9Y"},
  {"title": "Slime Rancher 2 (Original Game Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_lZkvKIZyR18ZHUPdUaiF1pmKRHjr6sovk"},
  {"title": "Minecraft: The Wild Update (Original Game Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_kZ2SAX1x6Nlf1qj_Z-RHB2he9uXXiuuNs"},
  {"title": "Roblox 3008, Vol. 1 (Original Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_ngNQsDqZlbbp5a-BZ6BhQF9VzwY1xDHIQ"},
  {"title": "UNDERTALE Soundtrack", "url": "https://music.youtube.com/playlist?list=OLAK5uy_ljXkQlhVlWyV7BxSxMMzgOLbzYS_-JPt4"},
  {"title": "Slime Rancher 2, Vol.2 (Original Game Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_m6f3H_Be9d-wgEZ8iexYbTl0Sk_koDAJY"},
  {"title": "Terraria (Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_mPd3bgeYqn1kYq4WcMkK81W_Ah0aEQypE"},
  {"title": "Running From The Internet, Vol. 1 (Original Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_klZxReMOuU562U-e9KldU3DDQsIhnMDxc"},
  {"title": "Minecraft: Nether Update (Original Game Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_lx3LhwbhstxzQcZIXqDBr7sNOjz5ZKr7A"},
  {"title": "Selected Ambient Works Volume II", "url": "https://music.youtube.com/playlist?list=OLAK5uy_lOxSWAQX3iFOW6dH_aU_FlFqxFQV42g84"},
  {"title": "DELTARUNE Chapter 2 (Original Game Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_m-rr6K-H8nfmI3MdSzCRpQw0gxDeG5jzk"},
  {"title": "DELTARUNE Chapter 1 (Original Game Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_kidGzGmzCUSJK1LAtIh7ngZwRF9MT3qjE"},
  {"title": "Slime Rancher (Original Game Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_kWMjW9nvHXHjIXgBPfQz3vP4E5jpFuaow"},
  {"title": "Drukqs", "url": "https://music.youtube.com/playlist?list=OLAK5uy_nG46LZ_uffzpRmfuooj3L0LGSJOMBOVQo"},
  {"title": "Selected Ambient Works 85-92", "url": "https://music.youtube.com/playlist?list=OLAK5uy_npVGHGqWs_-hTzVUivb8lCndQPVB7aIm0"},
  {"title": "The Foundation (Original Game Soundtrack), Vol. 2", "url": "https://music.youtube.com/playlist?list=OLAK5uy_krzWyMq_JgKyrDh-zjM7ry9oyusXyk0EY"},
  {"title": "DELTARUNE Chapters 3+4 (Original Game Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_k-fz2U2mTfcN9R63A7DyL6V_BDUOLpyiE"},
  {"title": "Minecraft Dungeons (Original Game Soundtrack)", "url": "https://music.youtube.com/playlist?list=OLAK5uy_lLkMYaC8VvsHDlzqKR1nX-ccJVKBdroWI"},
  {"title": "Slime Rancher (Original Game Soundtrack), Vol. 2", "url": "https://music.youtube.com/playlist?list=OLAK5uy_mbBdg2HkSefEsH2riHFIvBWaMrux0F64A"},
  {"title": "Syro", "url": "https://music.youtube.com/playlist?list=OLAK5uy_lYw1W8SsabxulshCqGJFlY71VGXedyooc"}
]

def sync_playlist(name, url, skip_filters=True, prefix=""):
    safe_name = sanitize_filename(name)
    target_dir = os.path.join(MUSIC_DIR, f"{prefix}{safe_name}")
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"\n--- Syncing: {name} ---")
    cmd = YT_DLP + [
        "-x", "--audio-format", "mp3",
        "--audio-quality", "0",
        "-f", "ba/b",
        "-o", f"{target_dir}/%(title)s.%(ext)s",
        "--download-archive", os.path.join(target_dir, "archive.txt"),
        "--cookies-from-browser", "firefox",
        "--js-runtimes", f"node:{NODE_PATH}",
        "--extractor-args", "youtube:player_client=web,android,ios;youtubetab:skip=authcheck",
        "--ignore-errors",
        "--embed-metadata",
        "--embed-thumbnail",
        "--convert-thumbnails", "jpg",
        "--ppa", "ThumbnailsConvertor:-qmin 1 -qmax 1",
        "--ppa", "ffmpeg: -mapping_family 0",
        "--ppa", "ffmpeg:-id3v2_version 3",
        "--parse-metadata", "%(album,playlist,playlist_title)s:%(album)s",
    ]
    
    if not skip_filters:
        cmd += ["--match-filters", "category = 'Music' | (artist & track & album)"]
    
    cmd.append(url)
    
    env = os.environ.copy()
    if os.path.exists(NODE_PATH):
        env["PATH"] = f"{os.path.dirname(NODE_PATH)}:{env.get('PATH', '')}"
    
    subprocess.run(cmd, env=env)

def print_usage():
    print("""
Usage: sync-music [OPTIONS]

Options:
  -h        Show this help message
  -e        Fast Edit Mode: Jump straight to the local metadata editor
  -m        Fast Manual Mode: Jump straight to manual URL entry
  -s SELECT Sync specific items by index (comma-separated, e.g., -s 1,3,5)
""")

def playlist_sync_menu(cached_items=None):
    items = cached_items
    if items is None:
        items = get_library_items()
    
    while True:
        print("\n--- Playlists ---")
        for i, item in enumerate(items, 1):
            print(f"[{i}] {item['title'] or '[Private Item]'}")
        
        print("\n[A] Sync ALL")
        print("[S] Re-Scan Library")
        print("[B] Back to Main Menu")
        
        choice = input("\nSelect numbers (e.g. 1,3) or 'A', 'S', 'B': ").strip().upper()
        if choice == 'B': return items
        if choice == 'S':
            items = get_library_items()
            continue
        if choice == 'A':
            for item in items: sync_playlist(item["title"] or "Unnamed", item["url"])
        else:
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(',') if x.strip().isdigit()]
                for i in indices:
                    if 0 <= i < len(items):
                        sync_playlist(items[i]["title"] or "Unnamed", items[i]["url"])
            except: pass
    return items

def album_sync_menu():
    while True:
        print("\n--- Albums ---")
        for i, album in enumerate(ALBUMS, 1):
            print(f"[{i}] {album['title']}")
        
        print("\n[A] Sync ALL")
        print("[B] Back to Main Menu")
        
        choice = input("\nSelect index or 'A', 'B': ").strip().upper()
        if choice == 'B': return
        if choice == 'A':
            for album in ALBUMS: sync_playlist(album["title"], album["url"], prefix="Album - ")
        else:
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(',') if x.strip().isdigit()]
                for i in indices:
                    if 0 <= i < len(ALBUMS):
                        sync_playlist(ALBUMS[i]["title"], ALBUMS[i]["url"], prefix="Album - ")
            except: pass

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    
    if "-h" in args:
        print_usage(); sys.exit(0)
    if "-e" in args:
        subprocess.run(["python3", os.path.join(os.getcwd(), "metadata_editor.py")]); sys.exit(0)
    if "-m" in args:
        url = input("URL: "); name = input("Folder Name: ")
        if url and name: sync_playlist(name, url); sys.exit(0)

    cached_playlists = None
    while True:
        print("\n=== YouTube Music Manager ===")
        print("[P] Sync Playlists")
        print("[A] Sync Albums")
        print("[E] Edit Local Metadata")
        print("[M] Manual URL Sync")
        print("[S] Scan Library (Refresh)")
        print("[Q] Quit")
        
        cmd = input("\nChoice: ").strip().upper()
        if cmd == 'Q': break
        elif cmd == 'E': subprocess.run(["python3", os.path.join(os.getcwd(), "metadata_editor.py")])
        elif cmd == 'A': album_sync_menu()
        elif cmd == 'P': cached_playlists = playlist_sync_menu(cached_playlists)
        elif cmd == 'S': cached_playlists = get_library_items()
        elif cmd == 'M':
            url = input("URL: "); name = input("Folder Name: ")
            if url and name: sync_playlist(name, url)
