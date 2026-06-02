#!/usr/bin/env python3
"""Purge expired sessions via the running API (memory backend is process-local)."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


def main() -> int:
    base = os.getenv("PIPELINE_URL", "http://127.0.0.1:8787").rstrip("/")
    url = f"{base}/admin/purge-expired"
    req = urllib.request.Request(url, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        print(
            f"purge-expired-sessions: HTTP {exc.code} from {url}\n{detail}",
            file=sys.stderr,
        )
        if exc.code == 404:
            print(
                "Hint: set ALLOW_ADMIN_PURGE=1 on the API server (see server/.env.example).",
                file=sys.stderr,
            )
        return 1
    except urllib.error.URLError as exc:
        print(
            f"purge-expired-sessions: cannot reach {url}: {exc.reason}\n"
            "Start the API (e.g. cd server && uv run uvicorn src.main:app --port 8787).",
            file=sys.stderr,
        )
        return 1

    purged = body.get("purged", 0)
    orphans = body.get("orphan_exports", 0)
    hours = os.getenv("AUTO_DELETE_HOURS", "24")
    print(
        f"Purged {purged} in-memory session(s) and {orphans} orphan export file(s) "
        f"(AUTO_DELETE_HOURS={hours})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
