"""API session flow with real pipeline (mocked LLM)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.main import app
from tests.test_pipeline import _litellm_side_effect, _mock_llm_responses

FIXTURE_RESUME = Path(__file__).resolve().parents[2] / "docs" / "fixtures" / "sample-resume.docx"
FIXTURE_JD = Path(__file__).resolve().parents[2] / "docs" / "fixtures" / "sample-jd.txt"
MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def test_session_flow_real_pipeline_mocked(monkeypatch):
    monkeypatch.setenv("USE_REAL_PIPELINE", "1")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    from src.config import config

    monkeypatch.setattr(config, "use_real_pipeline", True)
    monkeypatch.setattr(config.llm, "api_key", "test-key")

    resume_bytes = FIXTURE_RESUME.read_bytes()
    responses = _mock_llm_responses(resume_bytes)
    client = TestClient(app)

    with patch(
        "src.llm.client.litellm.completion",
        side_effect=_litellm_side_effect(responses),
    ):
        r = client.post(
            "/sessions",
            files={"resume": ("resume.docx", resume_bytes, MIME)},
            data={"jd_text": FIXTURE_JD.read_text(encoding="utf-8"), "consent": "true"},
        )
        assert r.status_code == 200, r.text
        sid = r.json()["session_id"]
        body = client.get(f"/sessions/{sid}").json()

    assert body["status"] == "ready", body.get("error")
    assert body["result"] is not None
    assert "matched" in body["result"]["gap_report"]
    assert "partial_match" in body["result"]["gap_report"]
    assert body["result"]["changes"]
    assert all(c.get("evidence_ids") for c in body["result"]["changes"])
