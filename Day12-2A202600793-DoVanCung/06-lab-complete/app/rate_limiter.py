"""Redis-backed sliding-window rate limiter with local fallback."""

import time
from collections import defaultdict, deque

from fastapi import HTTPException


class RateLimiter:
    def __init__(self, redis_client=None, max_requests: int = 10, window_seconds: int = 60):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._windows: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> dict:
        if self.redis:
            return self._check_redis(key)
        return self._check_memory(key)

    def _check_memory(self, key: str) -> dict:
        now = time.time()
        window = self._windows[key]
        while window and window[0] <= now - self.window_seconds:
            window.popleft()

        if len(window) >= self.max_requests:
            retry_after = max(1, int(window[0] + self.window_seconds - now) + 1)
            self._raise_limited(retry_after)

        window.append(now)
        return {
            "limit": self.max_requests,
            "remaining": self.max_requests - len(window),
            "reset_at": int(now + self.window_seconds),
        }

    def _check_redis(self, key: str) -> dict:
        now_ms = int(time.time() * 1000)
        window_ms = self.window_seconds * 1000
        redis_key = f"rate:{key}"

        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(redis_key, 0, now_ms - window_ms)
        pipe.zcard(redis_key)
        _, count = pipe.execute()

        if count >= self.max_requests:
            oldest = self.redis.zrange(redis_key, 0, 0, withscores=True)
            retry_after = self.window_seconds
            if oldest:
                retry_after = max(1, int((oldest[0][1] + window_ms - now_ms) / 1000) + 1)
            self._raise_limited(retry_after)

        pipe = self.redis.pipeline()
        pipe.zadd(redis_key, {str(now_ms): now_ms})
        pipe.expire(redis_key, self.window_seconds)
        pipe.zcard(redis_key)
        _, _, used = pipe.execute()
        return {
            "limit": self.max_requests,
            "remaining": max(0, self.max_requests - used),
            "reset_at": int(time.time() + self.window_seconds),
        }

    def _raise_limited(self, retry_after: int) -> None:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {self.max_requests} req/min",
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(self.max_requests),
                "X-RateLimit-Remaining": "0",
            },
        )
