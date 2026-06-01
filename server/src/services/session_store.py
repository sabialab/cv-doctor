"""P0 内存会话存储（本地开发）；生产由 Worker + D1/R2 替代。"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal

from src.p0_models import DiagnosisResult

SessionStatus = Literal["pending", "processing", "ready", "failed"]


@dataclass
class SessionRecord:
    session_id: str
    status: SessionStatus = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    resume_bytes: bytes = b""
    jd_text: str = ""
    result: DiagnosisResult | None = None
    error: str | None = None
    export_path: str | None = None


_lock = threading.Lock()
_sessions: dict[str, SessionRecord] = {}


def create_session(*, resume_bytes: bytes, jd_text: str) -> SessionRecord:
    session_id = str(uuid.uuid4())
    record = SessionRecord(
        session_id=session_id,
        status="pending",
        resume_bytes=resume_bytes,
        jd_text=jd_text,
    )
    with _lock:
        _sessions[session_id] = record
    return record


def get_session(session_id: str) -> SessionRecord | None:
    with _lock:
        return _sessions.get(session_id)


def update_session(session_id: str, **kwargs: object) -> SessionRecord | None:
    with _lock:
        rec = _sessions.get(session_id)
        if rec is None:
            return None
        for key, value in kwargs.items():
            setattr(rec, key, value)
        return rec


def delete_session(session_id: str) -> bool:
    with _lock:
        return _sessions.pop(session_id, None) is not None
