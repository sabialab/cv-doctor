from fastapi.testclient import TestClient

from src.main import app
from src.services import session_store


def test_get_session_includes_processing_step(monkeypatch):
    monkeypatch.setattr(session_store, "_sessions", {})
    rec = session_store.create_session(resume_bytes=b"x", jd_text="jd")
    session_store.update_session(
        rec.session_id, status="processing", processing_step="analyzing_jd"
    )
    client = TestClient(app)
    body = client.get(f"/sessions/{rec.session_id}").json()
    assert body["status"] == "processing"
    assert body["processing_step"] == "analyzing_jd"
