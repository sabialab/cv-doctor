"""Full pipeline integration test (mocked LLM)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.facts import build_evidence_store
from src.llm.client import LLMClient
from src.parser_resume import parse_resume
from src.pipeline import run_diagnosis

FIXTURE_RESUME = Path(__file__).resolve().parents[2] / "docs" / "fixtures" / "sample-resume.docx"
FIXTURE_JD = Path(__file__).resolve().parents[2] / "docs" / "fixtures" / "sample-jd.txt"


def _mock_llm_responses(resume_bytes: bytes):
    store = build_evidence_store(parse_resume(resume_bytes))
    fact_ids = [f.id for f in store.get_usable() if f.source.value == "resume"]
    fallback = fact_ids[0] if fact_ids else "fact-raw-0"
    skill_id = next((i for i in fact_ids if "skill" in i), fallback)
    exp_id = next((i for i in fact_ids if "exp" in i and "ach" in i), skill_id)

    jd_payload = {
        "title": "高级后端工程师",
        "company": "某科技",
        "description": "负责 API 与数据管道",
        "requirements": [
            {"text": "Python 3 年以上", "category": "experience", "is_mandatory": True},
            {"text": "FastAPI", "category": "hard_skill", "is_mandatory": True},
            {"text": "Kubernetes", "category": "hard_skill", "is_mandatory": False},
        ],
        "responsibilities": ["设计与维护 REST API", "参与数据管道建设"],
        "keywords": ["Python", "FastAPI", "PostgreSQL"],
        "hard_skills": ["Python", "FastAPI"],
        "soft_skills": [],
    }
    change_payload = {
        "changes": [
            {
                "section": "skills",
                "original": "Python, Django",
                "revised": "Python（3 年）, Django, FastAPI",
                "reason": "JD 要求 FastAPI",
                "evidence_ids": [skill_id],
                "risk_level": "low",
                "source_label": "来自 JD 关键词",
            },
            {
                "section": "experiences[0].achievements[0]",
                "original": "参与内部系统开发，使用 Python 维护业务 API",
                "revised": "使用 Python 开发 REST API，支撑内部业务系统",
                "reason": "对齐 API 职责",
                "evidence_ids": [exp_id],
                "risk_level": "medium",
                "source_label": "来自 JD 职责",
            },
        ]
    }
    return [
        MagicMock(choices=[MagicMock(message=MagicMock(content=json.dumps(jd_payload)))]),
        MagicMock(choices=[MagicMock(message=MagicMock(content=json.dumps(change_payload)))]),
    ]


def _litellm_side_effect(responses: list):
    iterator = iter(responses)

    def _call(*_args, **_kwargs):
        try:
            return next(iterator)
        except StopIteration as exc:
            raise AssertionError("litellm.completion called more than expected") from exc

    return _call


def test_run_diagnosis_mocked():
    assert FIXTURE_RESUME.is_file()
    resume_bytes = FIXTURE_RESUME.read_bytes()
    jd_text = FIXTURE_JD.read_text(encoding="utf-8")
    client = LLMClient(model="deepseek/deepseek-chat", api_key="test")
    responses = _mock_llm_responses(resume_bytes)

    with patch(
        "src.llm.client.litellm.completion",
        side_effect=_litellm_side_effect(responses),
    ):
        result = run_diagnosis(resume_bytes, jd_text, llm=client)

    assert result.jd_interpretation.role_summary
    assert result.jd_interpretation.responsibilities
    assert result.match_score.overall >= 0
    assert result.match_score.preferred_score == result.match_score.breakdown["preferred_score"]
    assert len(result.changes) <= 3
    assert all(c.evidence_ids for c in result.changes)
    assert result.model_used
