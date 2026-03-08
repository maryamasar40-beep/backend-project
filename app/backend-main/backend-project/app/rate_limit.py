import os

from fastapi import Depends, HTTPException, Request, status

from app.auth import get_current_user
from app.cache import get_redis

RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))


def limit_by_user_or_ip(scope: str):
    async def _dependency(request: Request, current_user=Depends(get_current_user)):
        if not RATE_LIMIT_ENABLED:
            return

        identity = f"user:{current_user.id}"
        ip = request.client.host if request.client else "unknown"
        key = f"rl:{scope}:{identity}:{ip}"

        try:
            redis = get_redis()
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, RATE_LIMIT_WINDOW_SECONDS)
            if count > RATE_LIMIT_REQUESTS:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                )
        except HTTPException:
            raise
        except Exception:
            return

    return _dependency


def limit_by_ip(scope: str):
    async def _dependency(request: Request):
        if not RATE_LIMIT_ENABLED:
            return

        ip = request.client.host if request.client else "unknown"
        key = f"rl:{scope}:ip:{ip}"

        try:
            redis = get_redis()
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, RATE_LIMIT_WINDOW_SECONDS)
            if count > RATE_LIMIT_REQUESTS:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                )
        except HTTPException:
            raise
        except Exception:
            return

    return _dependency
