import redis
import json

def get_redis_client():
    return redis.Redis(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True  # important: returns strings, not bytes
    )

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
