import os
import time

from django.conf import settings
from django.core.cache import cache


class RateLimitError(Exception):
    pass


def _should_skip() -> bool:
    env_skip = os.environ.get("SKIP_RATE_LIMIT", "").lower()
    if env_skip in ("1", "true", "yes"):
        return True
    return getattr(settings, "SKIP_RATE_LIMIT", False)


def check_rate_limit(key_prefix: str, max_attempts: int, window: int, request: object) -> None:
    if _should_skip():
        return
    ip = getattr(request, "META", {}).get("REMOTE_ADDR", "unknown")
    cache_key = f"ratelimit:{key_prefix}:{ip}"
    now = time.time()
    data = cache.get(cache_key, [])
    data = [t for t in data if t > now - window]
    if len(data) >= max_attempts:
        raise RateLimitError("Too many requests. Please try again later.")
    data.append(now)
    cache.set(cache_key, data, timeout=window)
