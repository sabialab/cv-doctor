"""API export trust boundary tests."""

from __future__ import annotations

import uuid
from io import BytesIO

from docx import Document
from fastapi.testclient import TestClient

from src.main import app
from src.models import Change, ChangeRisk, ChangeStatus
from src.services.session_store import create_session, update_session
from src.services.stub_pipeline import build_stub_diagnosis


def test_export_rejects_only_high_risk_accepted():
    client = TestClient(app)
    buf = BytesIO()
    Document().save(buf)
    rec = create_session(resume_bytes=buf.getvalue(), jd_text="test jd")
    result = build_stub_diagnosis()
    high = Change(
        id=str(uuid.uuid4()),
        section="exp",
        original="x",
        revised="y",
        reason="r",
        evidence_ids=["f1"],
        risk_level=ChangeRisk.HIGH,
        status=ChangeStatus.ACCEPTED,
    )
    result.changes = [high]
    update_session(rec.session_id, status="ready", result=result)

    e = client.post(f"/sessions/{rec.session_id}/export")
    assert e.status_code == 400
    assert "高风险" in e.json()["detail"]


def test_api_result_includes_evidence_ids():
    client = TestClient(app)
    buf = BytesIO()
    Document().save(buf)
    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    r = client.post(
        "/sessions",
        files={"resume": ("resume.docx", buf.getvalue(), mime)},
        data={"jd_text": "需要 Python"},
    )
    sid = r.json()["session_id"]
    body = client.get(f"/sessions/{sid}").json()
    assert body["status"] == "ready"
    for ch in body["result"]["changes"]:
        assert "evidence_ids" in ch
