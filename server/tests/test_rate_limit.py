"""POST /sessions rate limit (local direct API)."""

from io import BytesIO

from docx import Document
from fastapi.testclient import TestClient

from src.main import app
from src.services.rate_limit import RATE_LIMIT_DETAIL, reset_for_tests


def _session_form() -> dict[str, str]:
    return {
        "jd_text": "需要 Python 后端工程师。",
        "consent": "true",
    }


def _minimal_docx() -> bytes:
    buf = BytesIO()
    doc = Document()
    doc.add_paragraph("负责后端开发与维护。")
    doc.save(buf)
    return buf.getvalue()


def test_rate_limit_returns_429_with_fixed_detail(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "1")
    monkeypatch.setenv("RATE_LIMIT_SESSIONS_PER_DAY", "2")
    reset_for_tests()
    client = TestClient(app)
    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    files = {"resume": ("resume.docx", _minimal_docx(), mime)}

    assert client.post("/sessions", files=files, data=_session_form()).status_code == 200
    assert client.post("/sessions", files=files, data=_session_form()).status_code == 200
    blocked = client.post("/sessions", files=files, data=_session_form())
    assert blocked.status_code == 429
    assert blocked.json()["detail"] == RATE_LIMIT_DETAIL


def test_validation_failure_does_not_consume_rate_limit(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "1")
    monkeypatch.setenv("RATE_LIMIT_SESSIONS_PER_DAY", "1")
    reset_for_tests()
    client = TestClient(app)
    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    files = {"resume": ("resume.docx", _minimal_docx(), mime)}

    assert (
        client.post(
            "/sessions",
            files=files,
            data={"jd_text": "需要 Python", "consent": "false"},
        ).status_code
        == 400
    )
    assert client.post("/sessions", files=files, data=_session_form()).status_code == 200


def test_invalid_rate_limit_env_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "1")
    monkeypatch.setenv("RATE_LIMIT_SESSIONS_PER_DAY", "not-a-number")
    reset_for_tests()
    client = TestClient(app)
    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    files = {"resume": ("resume.docx", _minimal_docx(), mime)}
    assert client.post("/sessions", files=files, data=_session_form()).status_code == 200


def test_rate_limit_skipped_behind_worker(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "1")
    monkeypatch.setenv("RATE_LIMIT_SESSIONS_PER_DAY", "1")
    reset_for_tests()
    client = TestClient(app)
    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    files = {"resume": ("resume.docx", _minimal_docx(), mime)}
    headers = {"CF-Connecting-IP": "203.0.113.50"}

    assert (
        client.post("/sessions", files=files, data=_session_form(), headers=headers).status_code
        == 200
    )
    assert (
        client.post("/sessions", files=files, data=_session_form(), headers=headers).status_code
        == 200
    )
