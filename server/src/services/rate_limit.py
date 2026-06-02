"""Per-IP daily cap on POST /sessions (local direct API only)."""

from __future__ import annotations

import os
import threading
from datetime import UTC, datetime

from fastapi import Request

# Keep in sync with worker/src/rate_limit.ts
RATE_LIMIT_DETAIL = "今日创建会话次数已达上限，请明天再试。"


class RateLimitError(Exception):
    def __init__(self, detail: str = RATE_LIMIT_DETAIL) -> None:
        self.detail = detail
        super().__init__(detail)


_lock = threading.Lock()
_buckets: dict[str, tuple[str, int]] = {}


def _day_key() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d")


def _limit() -> int:
    return int(os.getenv("RATE_LIMIT_SESSIONS_PER_DAY", "20"))


def should_apply_rate_limit(request: Request) -> bool:
    """Skip when disabled or request already passed Worker edge limit."""
    flag = os.getenv("RATE_LIMIT_ENABLED", "1").strip().lower()
    if flag in ("0", "false", "no"):
        return False
    if request.headers.get("cf-connecting-ip"):
        return False
    return True


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def check_session_create_rate_limit(client_key: str) -> None:
    limit = _limit()
    if limit <= 0:
        return
    day = _day_key()
    with _lock:
        prev_day, count = _buckets.get(client_key, (day, 0))
        if prev_day != day:
            count = 0
        if count >= limit:
            raise RateLimitError()
        _buckets[client_key] = (day, count + 1)


def reset_for_tests() -> None:
    with _lock:
        _buckets.clear()
