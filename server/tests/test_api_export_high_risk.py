"""Export must not include high-risk accepted changes."""

from __future__ import annotations

import uuid
from io import BytesIO

from docx import Document
from fastapi.testclient import TestClient

from src.main import app
from src.models import Change, ChangeRisk, ChangeStatus
from src.p0_models import DiagnosisResult, PolicyGuardSummary
from src.services import session_store


def _minimal_docx() -> bytes:
    buf = BytesIO()
    doc = Document()
    doc.add_paragraph("负责后端开发与维护。")
    doc.save(buf)
    return buf.getvalue()


def test_export_rejects_only_high_risk_accepted(monkeypatch):
    monkeypatch.setattr(session_store, "_sessions", {})
    rec = session_store.create_session(resume_bytes=_minimal_docx(), jd_text="jd")
    high = Change(
        id=str(uuid.uuid4()),
        section="summary",
        original="负责后端开发与维护。",
        revised="主导全公司技术战略（扩大职责）。",
        reason="test",
        evidence_ids=["e1"],
        risk_level=ChangeRisk.HIGH,
        status=ChangeStatus.ACCEPTED,
    )
    session_store.update_session(
        rec.session_id,
        status="ready",
        result=DiagnosisResult(
            changes=[high],
            policy_guard=PolicyGuardSummary(passed=True),
        ),
    )
    client = TestClient(app)
    r = client.post(f"/sessions/{rec.session_id}/export")
    assert r.status_code == 400
    assert "高风险" in r.json()["detail"]
