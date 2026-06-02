"""Log filter must not emit full JD / resume / revised text."""

from __future__ import annotations

import logging

from src.logging_config import RedactingFilter, configure_logging


def test_redacting_filter_scrubs_sensitive_dict_args():
    filt = RedactingFilter()
    long_jd = "岗位" * 200
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="create session %s",
        args=({"jd_text": long_jd, "resume_bytes": b"x" * 5000, "session_id": "abc"},),
        exc_info=None,
    )
    assert filt.filter(record) is True
    payload = record.args[0] if isinstance(record.args, tuple) else record.args
    assert payload["jd_text"] == "<redacted>"
    assert payload["resume_bytes"] == "<redacted>"
    assert payload["session_id"] == "abc"


def test_redacting_filter_truncates_long_messages():
    filt = RedactingFilter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="x" * 500,
        args=(),
        exc_info=None,
    )
    filt.filter(record)
    assert "truncated" in record.msg
    assert len(record.msg) < 500


def test_configure_logging_is_idempotent():
    configure_logging()
    root = logging.getLogger()
    count = sum(1 for f in root.filters if isinstance(f, RedactingFilter))
    configure_logging()
    assert sum(1 for f in root.filters if isinstance(f, RedactingFilter)) == count
