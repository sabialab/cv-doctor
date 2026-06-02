# M3 log redaction (Task 4b)

Production/staging server logs use `RedactingFilter` (`server/src/logging_config.py`):

- Dict log args with keys `jd_text`, `resume_bytes`, `resume_text`, `revised`, `original` → `<redacted>` or byte length only.
- Plain log messages longer than 80 chars are truncated.

Task 11 `docs/deploy-p0-m3.md` §Operations should reference this note when the runbook is written.

**Worker rate limit (P0):** `worker/src/rate_limit.ts` uses an in-memory counter per isolate (not shared across cold starts). Treat as best-effort at the edge; durable KV/D1 is a follow-up if strict global caps are required.

**Local TTL purge:** Use `POST /admin/purge-expired` on the running API (`ALLOW_ADMIN_PURGE=1`) or `scripts/purge-expired-sessions.py`, which calls that endpoint. A separate Python process cannot see in-memory sessions.
