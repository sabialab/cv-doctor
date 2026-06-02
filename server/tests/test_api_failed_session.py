"""Failed session returns user-facing errors without stack traces."""

from io import BytesIO
from unittest.mock import patch

from docx import Document
from fastapi.testclient import TestClient

from src.llm.client import LLMError
from src.main import app


def _minimal_docx() -> bytes:
    buf = BytesIO()
    doc = Document()
    doc.add_paragraph("负责后端开发与维护。")
    doc.save(buf)
    return buf.getvalue()


def test_llm_error_surfaces_friendly_message():
    client = TestClient(app)
    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    files = {"resume": ("resume.docx", _minimal_docx(), mime)}
    data = {"jd_text": "需要 Python 的后端工程师。", "consent": "true"}

    with patch("src.main.config") as mock_config:
        mock_config.use_real_pipeline = True
        with patch("src.pipeline.run_diagnosis", side_effect=LLMError("api down")):
            sid = client.post("/sessions", files=files, data=data).json()["session_id"]

    body = client.get(f"/sessions/{sid}").json()
    assert body["status"] == "failed"
    assert body["error"]
    assert "Traceback" not in body["error"]
    assert "api down" not in body["error"]
