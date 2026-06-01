"""HTTP API DTOs — 与 src.models 解耦，仅暴露 P0 契约字段。"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from src.models import ChangeStatus
from src.p0_models import DiagnosisResult


class SessionCreateResponse(BaseModel):
    session_id: str
    status: Literal["pending", "processing", "ready", "failed"] = "pending"


class SessionStatusResponse(BaseModel):
    session_id: str
    status: Literal["pending", "processing", "ready", "failed"]
    result: dict[str, Any] | None = None
    error: str | None = None
    processing_step: str | None = None


class ChangePatchRequest(BaseModel):
    status: ChangeStatus | None = None
    revised: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_patch_body(self) -> ChangePatchRequest:
        if self.status is None and self.revised is None:
            raise ValueError("status 或 revised 至少提供一项")
        if self.status is not None and self.revised is not None:
            raise ValueError("revised 与 status 不能同时提供")
        return self


class ChangePatchResponse(BaseModel):
    id: str
    status: ChangeStatus


class ExportResponse(BaseModel):
    download_url: str
    format: Literal["txt", "docx"] = "docx"


class PrivacyResponse(BaseModel):
    message: str = "ok"


class ErrorResponse(BaseModel):
    detail: str


def diagnosis_result_for_api(result: DiagnosisResult) -> dict[str, Any]:
    """P0：对外最多 3 条 Change 建议，JSON 结构与前端 DiagnosisResult 对齐。"""
    changes = result.changes[:3]
    pg = result.policy_guard
    return {
        "jd_interpretation": result.jd_interpretation.model_dump(),
        "match_score": {
            "overall": result.match_score.overall,
            "status": result.match_score.status.value,
            "breakdown": result.match_score.breakdown,
        },
        "gap_report": {
            "matched": result.gap_report.matched,
            "partial_match": [
                g.model_dump(mode="json") for g in result.gap_report.partial_match
            ],
            "hard_missing": [g.model_dump(mode="json") for g in result.gap_report.hard_missing],
            "preferred_missing": [
                g.model_dump(mode="json") for g in result.gap_report.preferred_missing
            ],
            "keyword_missing": result.gap_report.keyword_missing,
            "total_gaps": result.gap_report.total_gaps,
        },
        "changes": [
            {
                "id": c.id,
                "section": c.section,
                "original": c.original,
                "revised": c.revised,
                "reason": c.reason,
                "evidence_ids": c.evidence_ids,
                "risk_level": c.risk_level.value
                if hasattr(c.risk_level, "value")
                else str(c.risk_level),
                "status": c.status.value if hasattr(c.status, "value") else str(c.status),
                "requires_user_confirmation": c.requires_user_confirmation,
                "source_label": c.source_label,
            }
            for c in changes
        ],
        "policy_guard": {
            "passed": pg.passed,
            "blocked_count": pg.blocked_count,
            "warnings": pg.warnings,
        },
        "free_change_limit": 3,
    }
