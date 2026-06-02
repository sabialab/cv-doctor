"""Redact resume/JD/revised content from application logs."""

from __future__ import annotations

import logging
from typing import Any

_SENSITIVE_KEYS = frozenset(
    {"jd_text", "resume_bytes", "resume_text", "revised", "original"}
)
_MAX_STR_LEN = 80


def _redact_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return f"<bytes len={len(value)}>"
    if isinstance(value, str) and len(value) > _MAX_STR_LEN:
        return f"<str len={len(value)}>"
    if isinstance(value, dict):
        return {
            k: ("<redacted>" if k in _SENSITIVE_KEYS else _redact_value(v))
            for k, v in value.items()
        }
    if isinstance(value, (list, tuple)):
        redacted = [_redact_value(v) for v in value]
        return type(value)(redacted)
    return value


def _redact_message(msg: str) -> str:
    if len(msg) <= _MAX_STR_LEN:
        return msg
    return f"{msg[:40]}…<truncated len={len(msg)}>"


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = _redact_message(record.msg)
        args = record.args
        if not args:
            return True
        if isinstance(args, dict):
            record.args = _redact_value(args)
        elif len(args) == 1 and isinstance(args[0], dict):
            record.args = (_redact_value(args[0]),)
        else:
            record.args = tuple(_redact_value(a) for a in args)
        return True


def configure_logging() -> None:
    root = logging.getLogger()
    if any(isinstance(f, RedactingFilter) for f in root.filters):
        return
    root.addFilter(RedactingFilter())
