"""Real diagnosis pipeline — parse → analyze → generate → map to P0 DTO."""

from __future__ import annotations

import time
from collections.abc import Callable

from src.change_generator import generate_changes
from src.config import config
from src.facts import build_evidence_store
from src.gap_analyzer import analyze_gaps
from src.llm.client import LLMClient, get_llm_client
from src.models import MatchLevel, Resume
from src.p0_models import (
    DiagnosisResult,
    GapItem,
    GapSeverity,
    GapType,
    JDInterpretation,
    MatchStatus,
    P0GapReport,
    P0MatchScore,
)
from src.parser_jd import parse_jd
from src.parser_resume import parse_resume, resume_from_raw_text
from src.processing_steps import (
    ANALYZING_JD,
    GENERATING_CHANGES,
    MATCHING,
    PARSING_RESUME,
)
from src.services.policy_guard import apply_policy_guard


def _match_status(overall: float) -> MatchStatus:
    if overall >= 75:
        return MatchStatus.STRONG
    if overall >= 50:
        return MatchStatus.PARTIAL
    return MatchStatus.WEAK


def _jd_interpretation(jd) -> JDInterpretation:
    hard = [r.text for r in jd.requirements if r.is_mandatory]
    preferred = [r.text for r in jd.requirements if not r.is_mandatory]
    responsibilities = jd.responsibilities or [r.text for r in jd.requirements[:5]]
    return JDInterpretation(
        role_summary=jd.description[:300] if jd.description else f"{jd.title} @ {jd.company}",
        hard_requirements=hard or jd.hard_skills,
        preferred_requirements=preferred or jd.soft_skills,
        keywords=jd.keywords,
        responsibilities=responsibilities[:5],
        nice_to_have=preferred,
    )


def _p0_gap_report(gap) -> P0GapReport:
    matched: list[str] = list(gap.strengths)
    partial_match: list[GapItem] = []
    hard_missing: list[GapItem] = []
    preferred_missing: list[GapItem] = []

    for req in gap.requirements_analysis:
        if req.match_level == MatchLevel.FULL:
            if req.text and req.text not in matched:
                matched.append(req.text)
            continue

        item = GapItem(
            requirement=req.text,
            severity=GapSeverity.HIGH if req.is_mandatory else GapSeverity.MEDIUM,
            suggestion=req.resume_evidence or "不能编造，仅可基于已有经历改写表达",
            gap_type=GapType.SKILL if req.category.value == "hard_skill" else GapType.OTHER,
        )

        if req.match_level == MatchLevel.PARTIAL:
            partial_match.append(item)
            continue

        if req.is_mandatory:
            hard_missing.append(item)
        else:
            preferred_missing.append(item)

    keyword_missing = [
        k.text
        for k in gap.requirements_analysis
        if k.match_level == MatchLevel.MISSING and k.category.value == "hard_skill"
    ][:5]

    return P0GapReport(
        matched=matched,
        partial_match=partial_match,
        hard_missing=hard_missing,
        preferred_missing=preferred_missing,
        keyword_missing=keyword_missing,
        responsibility_gaps=[g for g in gap.gaps if "缺失" in g][:5],
        overreach_risks=[],
        total_gaps=len(hard_missing) + len(preferred_missing) + len(partial_match),
    )


def _p0_match_score(gap) -> P0MatchScore:
    ms = gap.match_score
    overall = ms.overall
    return P0MatchScore(
        overall=overall,
        hard_requirement_score=ms.mandatory_coverage,
        preferred_score=ms.preferred_coverage,
        keyword_coverage=ms.keyword_coverage,
        responsibility_alignment=ms.experience_relevance,
        status=_match_status(overall),
        breakdown={
            "hard_requirement_score": ms.mandatory_coverage,
            "preferred_score": ms.preferred_coverage,
            "keyword_coverage": ms.keyword_coverage,
            "responsibility_alignment": ms.experience_relevance,
        },
    )


def _resolve_resume(resume_bytes: bytes, resume_text: str | None) -> Resume:
    if resume_bytes:
        resume = parse_resume(resume_bytes)
        if resume.raw_text.strip():
            return resume
        if resume_text and resume_text.strip():
            return resume_from_raw_text(resume_text)
        raise ValueError("无法从 DOCX 解析简历内容，请粘贴简历全文后重试")
    if resume_text and resume_text.strip():
        return resume_from_raw_text(resume_text)
    raise ValueError("请上传 .docx 或粘贴简历全文")


def run_diagnosis(
    resume_bytes: bytes,
    jd_text: str,
    *,
    resume_text: str | None = None,
    llm: LLMClient | None = None,
    on_step: Callable[[str], None] | None = None,
) -> DiagnosisResult:
    """Run full pipeline and return P0 DiagnosisResult."""

    def step(name: str) -> None:
        if on_step:
            on_step(name)

    started = time.perf_counter()
    client = llm or get_llm_client()

    step(PARSING_RESUME)
    resume = _resolve_resume(resume_bytes, resume_text)
    step(ANALYZING_JD)
    jd = parse_jd(jd_text, client)
    step(MATCHING)
    evidence = build_evidence_store(resume, jd)
    gap = analyze_gaps(resume, jd)
    step(GENERATING_CHANGES)
    change_set = generate_changes(resume, jd, gap, evidence, client, max_changes=3)
    changes, policy_summary = apply_policy_guard(change_set.changes)

    elapsed_ms = int((time.perf_counter() - started) * 1000)

    return DiagnosisResult(
        jd_interpretation=_jd_interpretation(jd),
        match_score=_p0_match_score(gap),
        gap_report=_p0_gap_report(gap),
        changes=changes,
        policy_guard=policy_summary,
        processing_time_ms=elapsed_ms,
        model_used=config.llm.model,
    )
