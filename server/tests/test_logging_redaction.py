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


def test_configure_logging_attaches_filter_to_handlers():
    configure_logging()
    root = logging.getLogger()
    assert root.handlers
    assert all(
        any(isinstance(f, RedactingFilter) for f in handler.filters)
        for handler in root.handlers
    )


def test_named_logger_emits_redacted_via_handler(caplog):
    configure_logging()
    caplog.set_level(logging.INFO)
    logger = logging.getLogger("src.services.diagnosis_errors")
    long_jd = "岗位" * 200
    logger.info("payload %s", {"jd_text": long_jd})
    assert long_jd not in caplog.text
    assert "<redacted>" in caplog.text or "len=" in caplog.text
