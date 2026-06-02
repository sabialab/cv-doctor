"""Local TTL purge for memory session backend."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.repositories.memory import memory_repository


@pytest.fixture(autouse=True)
def isolate_memory_sessions():
    from src.repositories.memory import _lock, _sessions

    with _lock:
        _sessions.clear()
    yield
    with _lock:
        _sessions.clear()


def test_purge_expired_deletes_session_and_export_file(tmp_path):
    repo = memory_repository()
    rec = repo.create_session(resume_bytes=b"x", jd_text="jd")
    export_dir = tmp_path / "exports"
    export_dir.mkdir()
    export_path = export_dir / f"{rec.session_id}.docx"
    export_path.write_bytes(b"docx")
    repo.update_session(rec.session_id, export_path=str(export_path))

    old = datetime.now(UTC) - timedelta(hours=25)
    repo.update_session(rec.session_id, created_at=old)

    before = datetime.now(UTC) - timedelta(hours=24)
    assert repo.purge_expired(before) == 1
    assert repo.get_session(rec.session_id) is None
    assert not export_path.exists()


def test_purge_expired_keeps_recent_sessions():
    repo = memory_repository()
    rec = repo.create_session(resume_bytes=b"x", jd_text="jd")
    before = datetime.now(UTC) - timedelta(hours=24)
    assert repo.purge_expired(before) == 0
    assert repo.get_session(rec.session_id) is not None


def test_admin_purge_expired_endpoint(monkeypatch, tmp_path):
    monkeypatch.setenv("ALLOW_ADMIN_PURGE", "1")
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    client = TestClient(app)
    repo = memory_repository()
    rec = repo.create_session(resume_bytes=b"x", jd_text="jd")
    old = datetime.now(UTC) - timedelta(hours=25)
    repo.update_session(rec.session_id, created_at=old)

    r = client.post("/admin/purge-expired")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["purged"] >= 1
    assert repo.get_session(rec.session_id) is None


def test_admin_purge_disabled_by_default():
    client = TestClient(app)
    assert client.post("/admin/purge-expired").status_code == 404
