import psycopg2
from psycopg2.extras import execute_values
from app.config import DATABASE_URL

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# conn = get_db_connection()
# cur = conn.cursor()

def insert_song(conn, cur, title: str, artist: str, duration: float) -> int:

    cur.execute(
        """
        INSERT INTO songs (title, artist, duration)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (title, artist, duration)
    )

    row = cur.fetchone()
    if row is None:
        raise RuntimeError("Insert failed, no ID returned")

    song_id = row[0]
    conn.commit()


    return song_id

def insert_fingerprints(
    conn,
    cur,
    fingerprints: list[tuple[str, int]],
    song_id: int
):

    values = [
        (hash_key, song_id, offset)
        for hash_key, offset in fingerprints
    ]

    execute_values(
        cur,
        """
        INSERT INTO fingerprints (hash, song_id, song_offset)
        VALUES %s
        """,
        values
    )

    conn.commit()
    
def get_song_metadata(cur, song_id: int):

    cur.execute(
        """
        SELECT title, artist
        FROM songs
        WHERE id = %s
        """,
        (song_id,)
    )

    result = cur.fetchone()

    return result

def get_stats(cur):
    cur.execute("SELECT COUNT(*) FROM songs")
    song_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM fingerprints")
    fingerprint_count = cur.fetchone()[0]

    avg_fps = (
        fingerprint_count / song_count
        if song_count > 0 else 0
    )

    return song_count, fingerprint_count, int(avg_fps)
