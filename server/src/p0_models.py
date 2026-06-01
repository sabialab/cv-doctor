"""P0 MVP 诊断结果模型（API / 桩流水线 / 前端对齐）。"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from src.models import Change


class MatchStatus(StrEnum):
    STRONG = "strong"
    PARTIAL = "partial"
    WEAK = "weak"


class GapSeverity(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GapType(StrEnum):
    EXPERIENCE = "experience"
    SKILL = "skill"
    KEYWORD = "keyword"
    OTHER = "other"


class JDInterpretation(BaseModel):
    role_summary: str = ""
    hard_requirements: list[str] = Field(default_factory=list)
    preferred_requirements: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    nice_to_have: list[str] = Field(default_factory=list)


class P0MatchScore(BaseModel):
    overall: float = Field(default=0.0, ge=0.0, le=100.0)
    hard_requirement_score: float = 0.0
    preferred_score: float = 0.0
    keyword_coverage: float = 0.0
    responsibility_alignment: float = 0.0
    status: MatchStatus = MatchStatus.PARTIAL
    breakdown: dict[str, float] = Field(default_factory=dict)


class GapItem(BaseModel):
    requirement: str
    severity: GapSeverity
    suggestion: str = ""
    gap_type: GapType = GapType.OTHER


class P0GapReport(BaseModel):
    matched: list[str] = Field(default_factory=list)
    partial_match: list[GapItem] = Field(default_factory=list)
    hard_missing: list[GapItem] = Field(default_factory=list)
    preferred_missing: list[GapItem] = Field(default_factory=list)
    keyword_missing: list[str] = Field(default_factory=list)
    responsibility_gaps: list[str] = Field(default_factory=list)
    overreach_risks: list[str] = Field(default_factory=list)
    total_gaps: int = 0


class PolicyGuardSummary(BaseModel):
    """桩流水线输出的策略摘要（与 v2 PolicyGuard 类区分）。"""

    passed: bool = True
    blocked_count: int = 0
    downgraded_count: int = 0
    blocked_items: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class DiagnosisResult(BaseModel):
    jd_interpretation: JDInterpretation = Field(default_factory=JDInterpretation)
    match_score: P0MatchScore = Field(default_factory=P0MatchScore)
    gap_report: P0GapReport = Field(default_factory=P0GapReport)
    changes: list[Change] = Field(default_factory=list)
    policy_guard: PolicyGuardSummary = Field(default_factory=PolicyGuardSummary)
    processing_time_ms: int = 0
    model_used: str = ""
