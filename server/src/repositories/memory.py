"""In-memory session repository (local dev)."""

from __future__ import annotations

import threading
import uuid
from datetime import datetime
from pathlib import Path

from src.models import ChangeStatus, PolicyAction, PolicyGuard
from src.repositories.session import PatchChangeResult, SessionRecord

_lock = threading.Lock()
_sessions: dict[str, SessionRecord] = {}
_SESSION_FIELDS = frozenset(SessionRecord.__dataclass_fields__)


class MemorySessionRepository:
    def create_session(
        self,
        *,
        resume_bytes: bytes,
        jd_text: str,
        resume_text: str | None = None,
    ) -> SessionRecord:
        session_id = str(uuid.uuid4())
        record = SessionRecord(
            session_id=session_id,
            status="pending",
            resume_bytes=resume_bytes,
            resume_text=resume_text,
            jd_text=jd_text,
        )
        with _lock:
            _sessions[session_id] = record
        return record

    def get_session(self, session_id: str) -> SessionRecord | None:
        with _lock:
            return _sessions.get(session_id)

    def update_session(self, session_id: str, **kwargs: object) -> SessionRecord | None:
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
        self,
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
                    ch.status = (
                        ChangeStatus.PENDING
                        if action == PolicyAction.NEEDS_CONFIRMATION
                        else ChangeStatus.ACCEPTED
                    )
                elif status is not None:
                    ch.status = ChangeStatus(status) if isinstance(status, str) else status
                return rec
            return None

    def delete_session(self, session_id: str) -> bool:
        with _lock:
            return _sessions.pop(session_id, None) is not None

    def list_expired_session_ids(self, before: datetime) -> list[str]:
        with _lock:
            return [
                sid for sid, rec in _sessions.items() if rec.created_at < before
            ]

    def purge_expired(self, before: datetime) -> int:
        with _lock:
            expired = [
                sid for sid, rec in _sessions.items() if rec.created_at < before
            ]
        for session_id in expired:
            self.clear_export_file(session_id)
            self.delete_session(session_id)
        return len(expired)

    def clear_export_file(self, session_id: str) -> None:
        rec = self.get_session(session_id)
        if rec is None or not rec.export_path:
            return
        Path(rec.export_path).unlink(missing_ok=True)
        self.update_session(session_id, export_path=None)


_memory_repo: MemorySessionRepository | None = None


def memory_repository() -> MemorySessionRepository:
    global _memory_repo
    if _memory_repo is None:
        _memory_repo = MemorySessionRepository()
    return _memory_repo
