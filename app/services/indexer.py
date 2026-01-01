from app.audio.preprocess import load_and_preprocess_audio
from app.audio.spectogram import compute_spectrogram
from app.audio.peaks import find_spectral_peaks
from app.audio.fingerprints import generate_fingerprints
from app.db.postgres import insert_song, insert_fingerprints

def index_song(
    file_path: str,
    title: str,
    artist: str
):
    # Step 1: preprocess
    audio, sr = load_and_preprocess_audio(file_path)
    duration = len(audio) / sr

    # Step 2: spectrogram
    S_db = compute_spectrogram(audio, sr)

    # Step 3: peak detection
    peaks = find_spectral_peaks(S_db)

    # Step 4: fingerprint hashing
    fingerprints = generate_fingerprints(peaks)

    # Step 5: database inserts
    song_id = insert_song(title, artist, duration)
    insert_fingerprints(fingerprints, song_id)

    print(
        f"Indexed '{title}' "
        f"({len(fingerprints)} fingerprints)"
    )
