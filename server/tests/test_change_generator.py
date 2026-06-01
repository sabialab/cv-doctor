"""Change generator evidence validation tests."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from src.change_generator import generate_changes
from src.llm.client import LLMClient
from src.models import EvidenceStore, Fact, FactSource, GapReport, JobDescription, Resume


def test_drops_hallucinated_evidence_ids():
    resume = Resume(name="T", raw_text="熟悉 Python", skills=["Python"])
    jd = JobDescription(title="后端", company="Co")
    gap = GapReport()
    store = EvidenceStore(
        facts=[Fact(id="fact-real", text="熟悉 Python", source=FactSource.RESUME)]
    )

    payload = {
        "changes": [
            {
                "section": "skills",
                "original": "熟悉 Python",
                "revised": "Python（3 年）",
                "reason": "对齐",
                "evidence_ids": ["fact-fake", "fact-real"],
                "risk_level": "low",
            }
        ]
    }
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps(payload)))]

    with patch("src.llm.client.litellm.completion", return_value=mock_response):
        client = LLMClient(model="deepseek/deepseek-chat", api_key="test")
        result = generate_changes(resume, jd, gap, store, client)

    assert len(result.changes) == 1
    assert result.changes[0].evidence_ids == ["fact-real"]


def test_drops_change_with_no_valid_evidence():
    resume = Resume(name="T", raw_text="text")
    jd = JobDescription(title="x", company="y")
    gap = GapReport()
    store = EvidenceStore()

    payload = {
        "changes": [
            {
                "section": "s",
                "original": "a",
                "revised": "b",
                "reason": "r",
                "evidence_ids": ["nonexistent"],
                "risk_level": "low",
            }
        ]
    }
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps(payload)))]

    with patch("src.llm.client.litellm.completion", return_value=mock_response):
        client = LLMClient(model="deepseek/deepseek-chat", api_key="test")
        result = generate_changes(resume, jd, gap, store, client)

    assert result.changes == []
