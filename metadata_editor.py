import os
import subprocess
import shutil

MUSIC_DIR = os.path.expanduser("~/Music")
# Check for common localized music directories
for local_dir in ["Музыка", "Musique", "Musik", "Musica"]:
    potential = os.path.expanduser(f"~/{local_dir}")
    if os.path.exists(potential):
        MUSIC_DIR = potential
        break

def get_folders():
    folders = [d for d in os.listdir(MUSIC_DIR) if os.path.isdir(os.path.join(MUSIC_DIR, d))]
    return sorted(folders)

def update_metadata(folder_path, album=None, artist=None, year=None):
    # Filter for valid .mp3 files, skipping temporary ones
    files = [f for f in os.listdir(folder_path) 
             if f.endswith(".mp3") and not f.endswith(".temp.mp3") and not f.endswith(".tmp.mp3")]
    if not files:
        print("No .mp3 files found in this folder.")
        return

    print(f"Preparing to update {len(files)} files...")
    
    for filename in files:
        file_path = os.path.join(folder_path, filename)
        temp_path = file_path + ".tmp.mp3"
        
        # Build FFmpeg command for metadata update
        # -i input -map 0 -c:a copy -metadata key=value output
        cmd = ["ffmpeg", "-i", file_path, "-map_metadata", "0", "-c", "copy"]
        
        if album:
            cmd += ["-metadata", f"album={album}"]
        if artist:
            cmd += ["-metadata", f"artist={artist}"]
            cmd += ["-metadata", f"album_artist={artist}"]
        if year:
            cmd += ["-metadata", f"date={year}"]
            
        cmd.append(temp_path)
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            os.replace(temp_path, file_path)
            print(f"  [DONE] {filename}")
        except subprocess.CalledProcessError as e:
            print(f"  [ERROR] Failed to update {filename}: {e.stderr.decode()}")
            if os.path.exists(temp_path):
                os.remove(temp_path)

def main():
    print("\n--- Local Music Metadata Editor ---")
    folders = get_folders()
    
    if not folders:
        print(f"No folders found in {MUSIC_DIR}")
        return

    print("\nSelect a folder to edit:")
    for i, folder in enumerate(folders):
        print(f"  [{i}] {folder}")
    
    while True:
        try:
            raw_input = input("\nEnter index (or -1 to cancel): ").strip()
            if not raw_input:
                continue
            choice = int(raw_input)
            
            if choice == -1:
                return
            if choice >= len(folders) or choice < 0:
                print(f"Index out of range. Please choose 0 to {len(folders)-1}")
                continue
            
            selected_folder = folders[choice]
            folder_path = os.path.join(MUSIC_DIR, selected_folder)
            
            print(f"\nEditing: {selected_folder}")
            print("Leave blank to keep existing value.")
            
            new_album = input("New Album Name: ").strip()
            new_artist = input("New Artist/Author: ").strip()
            new_year = input("New Year: ").strip()
            
            if not any([new_album, new_artist, new_year]):
                print("No changes specified. Exiting.")
                return

            confirm = input(f"\nApply changes to all tracks in '{selected_folder}'? (y/n): ").strip().lower()
            if confirm == 'y':
                update_metadata(folder_path, new_album or None, new_artist or None, new_year or None)
                print("\nBatch update complete!")
                break
            else:
                print("Action cancelled.")
                break
                
        except ValueError:
            print(f"Invalid input. Please enter a number between 0 and {len(folders)-1}")

if __name__ == "__main__":
    main()
