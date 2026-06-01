"""Gap analyzer heuristic tests."""

from __future__ import annotations

from src.gap_analyzer import analyze_gaps
from src.models import JobDescription, JobRequirement, MatchLevel, RequirementCategory, Resume


def test_analyze_gaps_matched_and_missing():
    resume = Resume(
        name="测试",
        raw_text="熟悉 Python 后端开发，使用 Django 构建 API",
        skills=["Python", "Django"],
    )
    jd = JobDescription(
        title="后端",
        company="Co",
        requirements=[
            JobRequirement(
                text="Python 3 年以上",
                category=RequirementCategory.EXPERIENCE,
                is_mandatory=True,
            ),
            JobRequirement(
                text="FastAPI 经验",
                category=RequirementCategory.HARD_SKILL,
                is_mandatory=True,
            ),
        ],
        keywords=["Python", "FastAPI"],
    )
    gap = analyze_gaps(resume, jd)
    levels = {r.text: r.match_level for r in gap.requirements_analysis}
    assert levels["Python 3 年以上"] in (MatchLevel.FULL, MatchLevel.PARTIAL)
    assert levels["FastAPI 经验"] == MatchLevel.MISSING
    assert gap.match_score.overall >= 0
    assert gap.match_score.preferred_coverage >= 0


def test_weak_token_match_is_missing_not_partial():
    resume = Resume(name="T", raw_text="做过数据分析", skills=[])
    jd = JobDescription(
        title="后端",
        company="Co",
        requirements=[
            JobRequirement(
                text="Kubernetes 容器编排平台经验",
                category=RequirementCategory.HARD_SKILL,
                is_mandatory=True,
            ),
        ],
    )
    gap = analyze_gaps(resume, jd)
    assert gap.requirements_analysis[0].match_level == MatchLevel.MISSING
