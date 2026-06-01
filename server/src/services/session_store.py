"""P0 内存会话存储（本地开发）；生产由 Worker + D1/R2 替代。"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal

from src.models import ChangeStatus, PolicyAction, PolicyGuard
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
    processing_step: str | None = None


PatchChangeResult = SessionRecord | Literal["forbidden"] | None

_lock = threading.Lock()
_sessions: dict[str, SessionRecord] = {}
_SESSION_FIELDS = frozenset(SessionRecord.__dataclass_fields__)


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
            if key not in _SESSION_FIELDS:
                raise ValueError(f"未知会话字段: {key}")
            setattr(rec, key, value)
        return rec


def patch_change(
    session_id: str,
    change_id: str,
    *,
    status: ChangeStatus | str | None = None,
    revised: str | None = None,
) -> PatchChangeResult:
    with _lock:
        rec = _sessions.get(session_id)
        if rec is None or rec.result is None:
            return None
        for ch in rec.result.changes:
            if ch.id != change_id:
                continue
            if revised is not None:
                trial = ch.model_copy(update={"revised": revised})
                action = PolicyGuard().check_change(trial)
                if action == PolicyAction.FORBIDDEN:
                    return "forbidden"
                ch.revised = revised
                if action == PolicyAction.NEEDS_CONFIRMATION:
                    ch.requires_user_confirmation = True
                ch.status = ChangeStatus.ACCEPTED
            elif status is not None:
                ch.status = ChangeStatus(status) if isinstance(status, str) else status
            return rec
        return None


def delete_session(session_id: str) -> bool:
    with _lock:
        return _sessions.pop(session_id, None) is not None
