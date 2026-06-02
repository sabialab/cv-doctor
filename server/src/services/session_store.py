"""Backward-compatible shim — prefer `src.repositories.get_repository()`."""

from __future__ import annotations

from datetime import datetime

from src.models import ChangeStatus

# Tests monkeypatch this alias; must reference the same dict as memory backend.
from src.repositories.memory import _sessions  # noqa: F401
from src.repositories.session import PatchChangeResult, SessionRecord
from src.repositories.session import get_repository as _get_repository


def _repo():
    return _get_repository()


def create_session(
    *,
    resume_bytes: bytes,
    jd_text: str,
    resume_text: str | None = None,
) -> SessionRecord:
    return _repo().create_session(
        resume_bytes=resume_bytes, jd_text=jd_text, resume_text=resume_text
    )


def get_session(session_id: str) -> SessionRecord | None:
    return _repo().get_session(session_id)


def update_session(session_id: str, **kwargs: object) -> SessionRecord | None:
    return _repo().update_session(session_id, **kwargs)


def patch_change(
    session_id: str,
    change_id: str,
    *,
    status: ChangeStatus | str | None = None,
    revised: str | None = None,
) -> PatchChangeResult:
    return _repo().patch_change(
        session_id, change_id, status=status, revised=revised
    )


def delete_session(session_id: str) -> bool:
    return _repo().delete_session(session_id)


def list_expired_session_ids(before: datetime) -> list[str]:
    return _repo().list_expired_session_ids(before)
