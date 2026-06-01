"""LiteLLM wrapper with structured JSON output and retry."""

from __future__ import annotations

import json
import logging
from typing import TypeVar

import litellm
from pydantic import BaseModel, ValidationError

from src.config import config

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMError(Exception):
    """LLM call or response parsing failed."""


class LLMClient:
    """Thin LiteLLM client for pipeline structured outputs."""

    def __init__(
        self,
        *,
        model: str | None = None,
        api_key: str | None = None,
        api_base: str | None = None,
    ) -> None:
        llm = config.llm
        self.model = model or llm.model
        self.api_key = api_key or llm.api_key
        self.api_base = api_base or llm.api_base

    def complete_json(
        self,
        *,
        system: str,
        user: str,
        schema: type[T],
        temperature: float | None = None,
        max_retries: int = 1,
    ) -> T:
        if not self.api_key:
            raise LLMError("未配置 LLM API Key（DEEPSEEK_API_KEY 或 CV_DOCTOR_LLM_API_KEY）")

        temp = temperature if temperature is not None else config.llm.temperature
        last_err: Exception | None = None

        for attempt in range(max_retries + 1):
            try:
                response = litellm.completion(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=temp,
                    max_tokens=config.llm.max_tokens,
                    api_key=self.api_key,
                    api_base=self.api_base or None,
                    response_format={"type": "json_object"},
                )
                raw = response.choices[0].message.content or ""
                data = json.loads(raw)
                return schema.model_validate(data)
            except (json.JSONDecodeError, ValidationError, IndexError, KeyError) as exc:
                last_err = exc
                logger.warning("LLM JSON parse attempt %s failed: %s", attempt + 1, exc)
            except Exception as exc:  # noqa: BLE001 — litellm raises varied types
                last_err = exc
                logger.warning("LLM call attempt %s failed: %s", attempt + 1, exc)

        raise LLMError("LLM 结构化输出失败，请稍后重试") from last_err


def get_llm_client() -> LLMClient:
    return LLMClient()
