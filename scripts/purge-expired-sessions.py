#!/usr/bin/env python3
"""Delete in-memory sessions older than AUTO_DELETE_HOURS (local dev / memory backend)."""

from __future__ import annotations

import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

_SERVER = Path(__file__).resolve().parents[1] / "server"
if str(_SERVER) not in sys.path:
    sys.path.insert(0, str(_SERVER))

from src.repositories.session import get_repository  # noqa: E402


def main() -> int:
    raw_hours = os.getenv("AUTO_DELETE_HOURS", "24")
    try:
        hours = int(raw_hours)
    except ValueError:
        print(f"Invalid AUTO_DELETE_HOURS={raw_hours!r}, using 24", file=sys.stderr)
        hours = 24

    before = datetime.now(UTC) - timedelta(hours=hours)
    try:
        repo = get_repository()
    except NotImplementedError as exc:
        print(f"purge-expired-sessions: {exc}", file=sys.stderr)
        return 1
    count = repo.purge_expired(before)
    print(f"Purged {count} session(s) created before {before.isoformat()} (>{hours}h ago)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
