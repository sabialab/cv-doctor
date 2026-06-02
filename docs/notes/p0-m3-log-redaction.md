# M3 log redaction (Task 4b)

Production/staging server logs use `RedactingFilter` (`server/src/logging_config.py`):

- Dict log args with keys `jd_text`, `resume_bytes`, `resume_text`, `revised`, `original` → `<redacted>` or byte length only.
- Plain log messages longer than 80 chars are truncated.

Task 11 `docs/deploy-p0-m3.md` §Operations should reference this note when the runbook is written.
