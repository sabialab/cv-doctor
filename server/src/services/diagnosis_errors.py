"""Map pipeline/LLM failures to user-visible Chinese messages."""

from __future__ import annotations

import logging

from pydantic import ValidationError

from src.llm.client import LLMError

logger = logging.getLogger(__name__)


def user_facing_diagnosis_error(exc: BaseException) -> str:
    if isinstance(exc, LLMError):
        return "分析服务暂时不可用，请稍后重试。若持续失败，请检查 API 配置或稍后再试。"
    if isinstance(exc, ValidationError):
        return "分析结果格式异常，请重试或更换岗位描述。"
    if isinstance(exc, TimeoutError):
        return "分析超时，请稍后重试。"
    logger.exception("diagnosis failed")
    return "分析失败，请稍后重试。"
