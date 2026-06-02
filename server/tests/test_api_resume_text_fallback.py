"""POST /sessions accepts resume_text without DOCX (stub pipeline)."""

from fastapi.testclient import TestClient

from src.main import app


def test_resume_text_only_session_ready():
    client = TestClient(app)
    r = client.post(
        "/sessions",
        data={
            "resume_text": "负责后端 API 设计与开发，熟悉 Python 与 FastAPI。",
            "jd_text": "招聘 Python 后端工程师，要求 FastAPI 经验。",
            "consent": "true",
        },
    )
    assert r.status_code == 200, r.text
    sid = r.json()["session_id"]
    body = client.get(f"/sessions/{sid}").json()
    assert body["status"] == "ready"
    assert body["result"] is not None
