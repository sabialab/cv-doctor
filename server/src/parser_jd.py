"""JD parser — LLM structured extraction to JobDescription."""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.llm.client import LLMClient
from src.llm.prompts import PARSER_JD_SYSTEM, PARSER_JD_USER
from src.models import JobDescription, JobRequirement, RequirementCategory


class _JDRequirementDraft(BaseModel):
    text: str
    category: str = "other"
    is_mandatory: bool = True


class _JDParserOutput(BaseModel):
    title: str = "未知岗位"
    company: str = "未知公司"
    location: str = ""
    description: str = ""
    requirements: list[_JDRequirementDraft] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    hard_skills: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)


_CATEGORY_MAP = {
    "hard_skill": RequirementCategory.HARD_SKILL,
    "soft_skill": RequirementCategory.SOFT_SKILL,
    "experience": RequirementCategory.EXPERIENCE,
    "education": RequirementCategory.EDUCATION,
    "certification": RequirementCategory.CERTIFICATION,
}


def _to_requirement(draft: _JDRequirementDraft) -> JobRequirement:
    cat = _CATEGORY_MAP.get(draft.category.lower(), RequirementCategory.OTHER)
    return JobRequirement(
        text=draft.text,
        category=cat,
        is_mandatory=draft.is_mandatory,
    )


def parse_jd(jd_text: str, llm: LLMClient | None = None) -> JobDescription:
    """Parse JD text via LLM into JobDescription."""
    client = llm or LLMClient()
    output = client.complete_json(
        system=PARSER_JD_SYSTEM,
        user=PARSER_JD_USER.format(jd_text=jd_text.strip()),
        schema=_JDParserOutput,
        temperature=0.1,
    )
    return JobDescription(
        title=output.title,
        company=output.company,
        location=output.location,
        description=output.description or jd_text[:500],
        requirements=[_to_requirement(r) for r in output.requirements],
        responsibilities=output.responsibilities,
        keywords=output.keywords,
        hard_skills=output.hard_skills,
        soft_skills=output.soft_skills,
    )
