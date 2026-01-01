import os
from app.services.indexer import index_song

SONGS_DIR = os.path.join(os.path.dirname(__file__), "../app/data/songs")
SONGS_DIR = os.path.abspath(SONGS_DIR)

for filename in os.listdir(SONGS_DIR):
    if not filename.lower().endswith((".mp3", ".wav", ".ogg")):
        continue

    path = os.path.join(SONGS_DIR, filename)

    # simple metadata extraction
    if " - " in filename:
        artist, title = filename.rsplit(".", 1)[0].split(" - ", 1)
    else:
        title = filename.rsplit(".", 1)[0]
        artist = "Unknown"

    print(f"Indexing: {title} by {artist}")
    index_song(path, title.strip(), artist.strip())
