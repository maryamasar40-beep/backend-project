import json
import os

from redis.asyncio import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_CACHE_TTL = int(os.getenv("REDIS_CACHE_TTL_SECONDS", "180"))

_redis_client: Redis | None = None


def get_redis() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=0.2,
            socket_timeout=0.2,
        )
    return _redis_client


async def get_cached_json(key: str) -> dict | None:
    client = get_redis()
    try:
        value = await client.get(key)
    except Exception:
        return None
    if value is None:
        return None
    return json.loads(value)


async def set_cached_json(key: str, payload: dict) -> None:
    client = get_redis()
    try:
        await client.setex(key, REDIS_CACHE_TTL, json.dumps(payload))
    except Exception:
        return
