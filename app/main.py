from fastapi import FastAPI, UploadFile, File, HTTPException
import tempfile
import os

from app.services.identifier import identify_song_redis
from app.db.postgres import get_db_connection
from app.db.redis_cache import get_redis_client
from app.db.postgres import get_song_metadata


app = FastAPI(
    title="Audio Fingerprint API",
    description="Shazam-like song identification service",
    version="1.0"
)

def get_resources():
    conn = get_db_connection()
    cur = conn.cursor()
    redis_client = get_redis_client()
    return conn, cur, redis_client

@app.post("/identify")
async def identify_song(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith((".wav", ".mp3", ".ogg")):
        raise HTTPException(status_code=400, detail="Unsupported audio format")

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    conn, cur, redis_client = get_resources()

    try:
        result = identify_song_redis(tmp_path, cur, redis_client)

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
        if not metadata:
            raise HTTPException(status_code=500, detail="Song metadata missing")

        title, artist = metadata

        return {
            "match": True,
            "song": {
                "title": title,
                "artist": artist
            },
            "confidence": score
        }

    finally:
        cur.close()
        conn.close()
        os.remove(tmp_path)

@app.get("/stats")
def stats():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT COUNT(*) FROM songs")
        songs_result = cur.fetchone()
        songs_indexed = songs_result[0] if songs_result else 0

        cur.execute("SELECT COUNT(*) FROM fingerprints")
        fingerprints_result = cur.fetchone()
        total_fingerprints = fingerprints_result[0] if fingerprints_result else 0

        avg_fps = (
            total_fingerprints / songs_indexed
            if songs_indexed > 0 else 0
        )

        return {
            "songs_indexed": songs_indexed,
            "total_fingerprints": total_fingerprints,
            "avg_fingerprints_per_song": int(avg_fps)
        }

    finally:
        cur.close()
        conn.close()

@app.get("/health")
def health():
    postgres_status = "ok"
    redis_status = "ok"

    # Check PostgreSQL
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()
        conn.close()
    except Exception:
        postgres_status = "down"

    # Check Redis
    try:
        redis_client = get_redis_client()
        redis_client.ping()
    except Exception:
        redis_status = "down"

    overall_status = (
        "ok"
        if postgres_status == "ok" and redis_status == "ok"
        else "degraded"
    )

    return {
        "status": overall_status,
        "postgres": postgres_status,
        "redis": redis_status
    }
