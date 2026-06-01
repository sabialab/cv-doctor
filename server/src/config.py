"""CV-Doctor 配置管理"""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class LLMConfig(BaseModel):
    """LLM 配置"""

    provider: str = Field(
        default_factory=lambda: os.getenv("CV_DOCTOR_LLM_PROVIDER", "openai")
    )
    model: str = Field(
        default_factory=lambda: os.getenv("CV_DOCTOR_LLM_MODEL", "gpt-4o")
    )
    temperature: float = 0.3
    max_tokens: int = 4096


class CollectorConfig(BaseModel):
    """数据采集配置"""

    tianyancha_api_key: str = Field(
        default_factory=lambda: os.getenv("TIANYANCHA_API_KEY", "")
    )
    boss_cookie: str = Field(
        default_factory=lambda: os.getenv("BOSS_COOKIE", "")
    )
    request_delay_min: float = 1.0  # 最小请求间隔（秒）
    request_delay_max: float = 3.0  # 最大请求间隔（秒）


class OutputConfig(BaseModel):
    """输出配置"""

    output_dir: Path = Field(
        default_factory=lambda: Path(
            os.getenv("CV_DOCTOR_OUTPUT_DIR", "./output")
        )
    )
    default_format: str = Field(
        default_factory=lambda: os.getenv("CV_DOCTOR_DEFAULT_FORMAT", "pdf")
    )


class AppConfig(BaseModel):
    """应用总配置"""

    llm: LLMConfig = Field(default_factory=LLMConfig)
    collector: CollectorConfig = Field(default_factory=CollectorConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    debug: bool = Field(
        default_factory=lambda: os.getenv("CV_DOCTOR_DEBUG", "false").lower() == "true"
    )


# 全局配置实例
config = AppConfig()
