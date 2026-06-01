"""LLM client unit tests (mocked, no API calls)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from src.llm.client import LLMClient, LLMError


class _SampleSchema(BaseModel):
    title: str
    count: int = 0


def test_complete_json_success():
    payload = {"title": "工程师", "count": 2}
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps(payload)))]

    with patch("src.llm.client.litellm.completion", return_value=mock_response):
        client = LLMClient(model="deepseek/deepseek-chat", api_key="test-key")
        result = client.complete_json(
            system="sys",
            user="user",
            schema=_SampleSchema,
            max_retries=0,
        )

    assert result.title == "工程师"
    assert result.count == 2


def test_complete_json_retries_on_invalid_json():
    bad = MagicMock()
    bad.choices = [MagicMock(message=MagicMock(content="not json"))]
    good = MagicMock()
    good.choices = [MagicMock(message=MagicMock(content='{"title":"ok"}'))]

    with patch(
        "src.llm.client.litellm.completion",
        side_effect=[bad, good],
    ):
        client = LLMClient(model="deepseek/deepseek-chat", api_key="test-key")
        result = client.complete_json(
            system="s",
            user="u",
            schema=_SampleSchema,
            max_retries=1,
        )

    assert result.title == "ok"


def test_complete_json_no_api_key():
    client = LLMClient(model="m", api_key="")
    with pytest.raises(LLMError, match="API Key"):
        client.complete_json(system="s", user="u", schema=_SampleSchema)
