from app.audio.preprocess import load_and_preprocess_audio
from app.audio.spectogram import compute_spectrogram
from app.audio.peaks import find_spectral_peaks
from app.audio.fingerprints import generate_fingerprints
from app.db.redis_cache import fetch_matches_with_cache, get_redis_client
from app.db.postgres import get_db_connection, get_song_metadata
from collections import defaultdict, Counter

MIN_AUDIO_DURATION = 5.0  # seconds
MIN_PEAKS = 200  # tuneable, good starting point
MIN_MATCH_SCORE = 30  # tuneable, start here
DOMINANCE_RATIO = 1.5  # tuneable, 1.4–1.8 typical

def identify_song_redis(file_path: str, cur, redis_client):
    audio, sr = load_and_preprocess_audio(file_path)
    

    duration = len(audio) / sr
    if duration < MIN_AUDIO_DURATION:
        return {
            "match": False,
            "reason": "Audio too short"
        }
    
    S_db = compute_spectrogram(audio, sr)
    peaks = find_spectral_peaks(S_db)
    

    if len(peaks) < MIN_PEAKS:
        return {
            "match": False,
            "reason": "Insufficient audio signal"
        }

    
    query_fps = generate_fingerprints(peaks)

    offset_votes = defaultdict(Counter)

    for hash_key, query_offset in query_fps:
        matches = fetch_matches_with_cache(
            cur, redis_client, hash_key
        )

        for song_id, db_offset in matches:
            delta = db_offset - query_offset
            offset_votes[song_id][delta] += 1

    if not offset_votes:
        return None

    # return list of (song_id, score)
    scores = [
        (song_id, max(counter.values()))
        for song_id, counter in offset_votes.items()
    ]

    scores.sort(key=lambda x: x[1], reverse=True)

    song_id, best_score = scores[0]

    # Fix 3: minimum absolute strength
    if best_score < MIN_MATCH_SCORE:
        return {
            "match": False,
            "reason": "Low confidence match"
        }

    # Fix 4: dominance ratio check
    if len(scores) > 1:
        second_best_score = scores[1][1]

        if best_score < DOMINANCE_RATIO * second_best_score:
            return {
                "match": False,
                "reason": "Ambiguous match"
            }

    return scores

def identify_and_display_redis(file_path: str):
    conn = get_db_connection()
    cur = conn.cursor()
    redis_client = get_redis_client()

    try:
        result = identify_song_redis(file_path, cur, redis_client)
        print("Results:", result)

        # Case 1: Rejection from backend (Fix 1–4)
        if isinstance(result, dict):
            return result

        # Case 2: No matches at all
        if not result:
            return {
                "match": False,
                "reason": "No match found"
            }

        # Case 3: Valid match list
        song_id, score = result[0]

        metadata = get_song_metadata(cur, song_id)
        if metadata is None:
            print("Metadata not found for song id:", song_id)
            return

        title, artist = metadata

        print("🎵 Match found")
        print("Title :", title)
        print("Artist:", artist)
        print("Score :", score)

    finally:
        cur.close()
        conn.close()
