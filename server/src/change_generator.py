"""Generate evidence-based resume changes via LLM."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from src.llm.client import LLMClient
from src.llm.prompts import CHANGE_GENERATOR_SYSTEM, CHANGE_GENERATOR_USER
from src.models import (
    Change,
    ChangeRisk,
    ChangeSet,
    ChangeStatus,
    EvidenceStore,
    GapReport,
    JobDescription,
    MatchLevel,
    Resume,
)


class _ChangeDraft(BaseModel):
    section: str
    original: str
    revised: str
    reason: str
    evidence_ids: list[str] = Field(default_factory=list)
    risk_level: str = "low"
    source_label: str = ""


class _ChangeDraftSet(BaseModel):
    changes: list[_ChangeDraft] = Field(default_factory=list)


_RISK_MAP = {
    "low": ChangeRisk.LOW,
    "medium": ChangeRisk.MEDIUM,
    "high": ChangeRisk.HIGH,
}


def _valid_evidence_ids(store: EvidenceStore, ids: list[str]) -> list[str]:
    return [eid for eid in ids if store.get_by_id(eid) is not None]


def _resume_summary(resume: Resume) -> str:
    parts = [resume.summary] if resume.summary else []
    for exp in resume.experiences[:3]:
        parts.append(f"{exp.company}|{exp.title}: {'; '.join(exp.achievements[:3])}")
    if resume.skills:
        parts.append("技能：" + ", ".join(resume.skills[:15]))
    return "\n".join(parts) or resume.raw_text[:800]


def _gap_lines(gap: GapReport) -> str:
    lines = [g for g in gap.gaps[:8]]
    for req in gap.requirements_analysis:
        if req.match_level == MatchLevel.PARTIAL:
            lines.append(f"部分匹配：{req.text}（证据：{req.resume_evidence or '弱'}）")
    return "\n".join(lines) or "无明显缺口"


def _evidence_list(store: EvidenceStore) -> str:
    usable = [f for f in store.get_usable() if f.source.value == "resume"]
    return "\n".join(f"- {f.id}: {f.text}" for f in usable[:30])


def generate_changes(
    resume: Resume,
    jd: JobDescription,
    gap: GapReport,
    evidence: EvidenceStore,
    llm: LLMClient | None = None,
    *,
    max_changes: int = 3,
) -> ChangeSet:
    """Generate ≤max_changes Change items grounded in evidence."""
    client = llm or LLMClient()
    hard_reqs = "\n".join(
        r.text for r in jd.requirements if r.is_mandatory
    ) or "（未提取）"

    output = client.complete_json(
        system=CHANGE_GENERATOR_SYSTEM,
        user=CHANGE_GENERATOR_USER.format(
            title=jd.title,
            company=jd.company,
            hard_reqs=hard_reqs,
            resume_summary=_resume_summary(resume),
            gaps=_gap_lines(gap),
            evidence_list=_evidence_list(evidence),
        ),
        schema=_ChangeDraftSet,
        temperature=0.3,
    )

    changes: list[Change] = []
    for draft in output.changes[:max_changes]:
        validated_ids = _valid_evidence_ids(evidence, draft.evidence_ids)
        if not validated_ids:
            continue
        risk = _RISK_MAP.get(draft.risk_level.lower(), ChangeRisk.LOW)
        changes.append(
            Change(
                id=str(uuid.uuid4()),
                section=draft.section,
                original=draft.original,
                revised=draft.revised,
                reason=draft.reason,
                evidence_ids=validated_ids,
                risk_level=risk,
                status=ChangeStatus.PENDING,
                requires_user_confirmation=risk != ChangeRisk.LOW,
                source_label=draft.source_label or "来自 JD 分析",
            )
        )

    return ChangeSet(changes=changes)
