"""JD parser tests (mocked LLM)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from src.llm.client import LLMClient
from src.parser_jd import parse_jd


def test_parse_jd_mock():
    payload = {
        "title": "高级后端工程师",
        "company": "某科技",
        "requirements": [
            {"text": "Python 3 年以上", "category": "experience", "is_mandatory": True},
            {"text": "FastAPI", "category": "hard_skill", "is_mandatory": True},
        ],
        "keywords": ["Python", "FastAPI"],
        "hard_skills": ["Python"],
        "soft_skills": [],
    }
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps(payload)))]

    with patch("src.llm.client.litellm.completion", return_value=mock_response):
        client = LLMClient(model="deepseek/deepseek-chat", api_key="test")
        jd = parse_jd("需要 Python 的后端", client)

    assert jd.title == "高级后端工程师"
    assert len(jd.requirements) == 2
    assert jd.keywords == ["Python", "FastAPI"]
