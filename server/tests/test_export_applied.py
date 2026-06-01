"""Export must apply at least one text replacement."""

from __future__ import annotations

import uuid
from io import BytesIO

from docx import Document
from fastapi.testclient import TestClient

from src.main import app
from src.models import Change, ChangeRisk, ChangeStatus
from src.services.session_store import create_session, update_session
from src.services.stub_pipeline import build_stub_diagnosis


def test_export_fails_when_no_text_replaced():
    client = TestClient(app)
    buf = BytesIO()
    Document().save(buf)
    rec = create_session(resume_bytes=buf.getvalue(), jd_text="jd")
    result = build_stub_diagnosis()
    result.changes = [
        Change(
            id=str(uuid.uuid4()),
            section="x",
            original="这段文字不在空简历里",
            revised="改后",
            reason="r",
            evidence_ids=["stub-evidence-summary"],
            risk_level=ChangeRisk.LOW,
            status=ChangeStatus.ACCEPTED,
        )
    ]
    update_session(rec.session_id, status="ready", result=result)

    e = client.post(f"/sessions/{rec.session_id}/export")
    assert e.status_code == 400
    assert "未在简历中找到" in e.json()["detail"]
