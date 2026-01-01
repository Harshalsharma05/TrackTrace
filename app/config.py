import os

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

if not REDIS_URL:
    raise RuntimeError("REDIS_URL is not set")
