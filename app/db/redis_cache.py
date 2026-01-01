import redis
import json
from app.config import REDIS_URL

def get_redis_client():
    return redis.from_url(REDIS_URL, decode_responses=True)

def fetch_matches_with_cache(cur, redis_client, hash_key: str):
    redis_key = f"fp:{hash_key}"

    cached = redis_client.get(redis_key)
    if cached is not None:
        return json.loads(cached)

    cur.execute(
        """
        SELECT song_id, song_offset
        FROM fingerprints
        WHERE hash = %s
        """,
        (hash_key,)
    )
    rows = cur.fetchall()

    redis_client.set(redis_key, json.dumps(rows))
    return rows
