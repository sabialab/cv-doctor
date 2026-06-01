"""Gap analysis and match scoring."""

from __future__ import annotations

import re

from src.models import GapReport, JobDescription, JobRequirement, MatchLevel, MatchScore, Resume


def _normalize(text: str) -> str:
    return re.sub(r"\s+", "", text.lower())


def _keyword_in_text(keyword: str, corpus: str) -> bool:
    kw = _normalize(keyword)
    if len(kw) < 2:
        return False
    return kw in _normalize(corpus)


def _match_requirement(req: JobRequirement, corpus: str) -> MatchLevel:
    if _keyword_in_text(req.text, corpus):
        return MatchLevel.FULL

    tokens = re.findall(r"[\w\u4e00-\u9fff]{2,}", req.text)
    if not tokens:
        return MatchLevel.MISSING

    hits = sum(1 for t in tokens if _keyword_in_text(t, corpus))
    if hits == 0:
        return MatchLevel.MISSING

    ratio = hits / len(tokens)
    min_hits = max(2, int(len(tokens) * 0.1))
    if ratio >= 0.5 or (ratio >= 0.2 and hits >= min_hits):
        return MatchLevel.PARTIAL
    return MatchLevel.MISSING


def _score_requirements(requirements: list[JobRequirement]) -> tuple[float, float]:
    if not requirements:
        return 70.0, 70.0
    mandatory = [r for r in requirements if r.is_mandatory]
    preferred = [r for r in requirements if not r.is_mandatory]

    def avg_level(reqs: list[JobRequirement]) -> float:
        if not reqs:
            return 70.0
        weights = {MatchLevel.FULL: 100, MatchLevel.PARTIAL: 55, MatchLevel.MISSING: 0}
        return sum(weights[r.match_level] for r in reqs) / len(reqs)

    return avg_level(mandatory), avg_level(preferred)


def _keyword_coverage(jd: JobDescription, corpus: str) -> float:
    keywords = jd.keywords or jd.hard_skills
    if not keywords:
        return 60.0
    hits = sum(1 for kw in keywords if _keyword_in_text(kw, corpus))
    return round(hits / len(keywords) * 100, 1)


def analyze_gaps(resume: Resume, jd: JobDescription) -> GapReport:
    """Match JD requirements against resume text and compute MatchScore."""
    corpus = resume.raw_text
    if resume.skills:
        corpus += "\n" + " ".join(resume.skills)
    for exp in resume.experiences:
        corpus += f"\n{exp.company} {exp.title} {' '.join(exp.achievements)}"

    analyzed: list[JobRequirement] = []
    strengths: list[str] = []
    gaps: list[str] = []

    for req in jd.requirements:
        level = _match_requirement(req, corpus)
        evidence = ""
        if level == MatchLevel.FULL:
            strengths.append(req.text)
            for token in re.findall(r"[\w\u4e00-\u9fff]{2,}", req.text):
                if _keyword_in_text(token, corpus):
                    evidence = token
                    break
        elif level == MatchLevel.PARTIAL:
            gaps.append(f"部分匹配：{req.text}")
        else:
            gaps.append(f"缺失：{req.text}")

        analyzed.append(
            req.model_copy(update={"match_level": level, "resume_evidence": evidence})
        )

    mandatory_cov, preferred_cov = _score_requirements(analyzed)
    kw_cov = _keyword_coverage(jd, corpus)

    experience_reqs = [r for r in analyzed if r.category.value == "experience"]
    if experience_reqs:
        experience_hits = sum(1 for r in experience_reqs if r.match_level != MatchLevel.MISSING)
        exp_rel = round(experience_hits / len(experience_reqs) * 100, 1)
        exp_weight = 0.25
    else:
        exp_rel = 70.0
        exp_weight = 0.0

    overall = round(
        mandatory_cov * 0.35
        + preferred_cov * 0.15
        + kw_cov * 0.25
        + exp_rel * exp_weight
        + (70.0 * (0.25 - exp_weight) if exp_weight == 0 else 0),
        1,
    )

    match_score = MatchScore(
        overall=min(overall, 100.0),
        mandatory_coverage=mandatory_cov,
        preferred_coverage=preferred_cov,
        keyword_coverage=kw_cov,
        experience_relevance=exp_rel,
        expression_quality=70.0,
    )

    return GapReport(
        match_score=match_score,
        requirements_analysis=analyzed,
        strengths=strengths,
        gaps=gaps,
        suggestions=[f"建议补充：{g}" for g in gaps[:5]],
    )
