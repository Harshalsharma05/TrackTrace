
import os
from mutagen import File

SONGS_DIR = os.path.join(os.path.dirname(__file__), '../app/data/songs')
SONGS_DIR = os.path.abspath(SONGS_DIR)

for filename in os.listdir(SONGS_DIR):
    file_path = os.path.join(SONGS_DIR, filename)
    if not os.path.isfile(file_path):
        continue
    name, ext = os.path.splitext(filename)
    # Skip files without audio extensions
    if ext.lower() not in ['.mp3', '.wav', '.ogg']:
        continue
    # Extract song name from 'Unknown - NAME.ext'
    if name.lower().startswith('unknown - '):
        song_name = name[10:].strip()
    else:
        song_name = name

    # Try to extract artist from metadata
    artist = "Unknown"
    try:
        audio = File(file_path, easy=True)
        if audio is not None:
            for tag in ("artist", "ARTIST", "TPE1", "albumartist", "ALBUMARTIST", "TPE2", "contributing artist", "CONTRIBUTING ARTIST", "Contributing artists"):
                if tag in audio:
                    value = audio[tag]
                    if isinstance(value, list):
                        value = value[0]
                    if value:
                        artist = str(value)
                        break
    except Exception as e:
        print(f"Warning: Could not read metadata for '{filename}': {e}")

    new_name = f"{artist} - {song_name}{ext}"
    new_path = os.path.join(SONGS_DIR, new_name)
    if filename != new_name:
        print(f"Renaming '{filename}' to '{new_name}'")
        os.rename(file_path, new_path)
print("Renaming complete.")
