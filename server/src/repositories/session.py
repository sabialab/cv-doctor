"""Session repository protocol and factory."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal, Protocol

from src.models import ChangeStatus
from src.p0_models import DiagnosisResult

SessionStatus = Literal["pending", "processing", "ready", "failed"]


@dataclass
class SessionRecord:
    session_id: str
    status: SessionStatus = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    resume_bytes: bytes = b""
    resume_text: str | None = None
    jd_text: str = ""
    result: DiagnosisResult | None = None
    error: str | None = None
    export_path: str | None = None
    processing_step: str | None = None


PatchChangeResult = SessionRecord | Literal["forbidden"] | None


class SessionRepository(Protocol):
    def create_session(
        self,
        *,
        resume_bytes: bytes,
        jd_text: str,
        resume_text: str | None = None,
    ) -> SessionRecord: ...

    def get_session(self, session_id: str) -> SessionRecord | None: ...

    def update_session(self, session_id: str, **kwargs: object) -> SessionRecord | None: ...

    def patch_change(
        self,
        session_id: str,
        change_id: str,
        *,
        status: ChangeStatus | str | None = None,
        revised: str | None = None,
    ) -> PatchChangeResult: ...

    def delete_session(self, session_id: str) -> bool: ...

    def list_expired_session_ids(self, before: datetime) -> list[str]: ...

    def clear_export_file(self, session_id: str) -> None: ...


def get_repository() -> SessionRepository:
    backend = os.getenv("SESSION_BACKEND", "memory").lower()
    if backend == "cloudflare":
        raise NotImplementedError("SESSION_BACKEND=cloudflare 尚未实现（见 M3 Task 9c）")
    from src.repositories.memory import memory_repository

    return memory_repository()
