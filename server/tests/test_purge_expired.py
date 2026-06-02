"""Local TTL purge for memory session backend."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from src.repositories.memory import _lock, _sessions, memory_repository


def test_purge_expired_deletes_session_and_export_file(tmp_path):
    repo = memory_repository()
    rec = repo.create_session(resume_bytes=b"x", jd_text="jd")
    export_dir = tmp_path / "exports"
    export_dir.mkdir()
    export_path = export_dir / f"{rec.session_id}.docx"
    export_path.write_bytes(b"docx")
    repo.update_session(rec.session_id, export_path=str(export_path))

    old = datetime.now(UTC) - timedelta(hours=25)
    with _lock:
        _sessions[rec.session_id].created_at = old

    before = datetime.now(UTC) - timedelta(hours=24)
    assert repo.purge_expired(before) == 1
    assert repo.get_session(rec.session_id) is None
    assert not export_path.exists()


def test_purge_expired_keeps_recent_sessions():
    repo = memory_repository()
    rec = repo.create_session(resume_bytes=b"x", jd_text="jd")
    try:
        before = datetime.now(UTC) - timedelta(hours=24)
        assert repo.purge_expired(before) == 0
        assert repo.get_session(rec.session_id) is not None
    finally:
        repo.clear_export_file(rec.session_id)
        repo.delete_session(rec.session_id)
