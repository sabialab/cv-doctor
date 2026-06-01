"""Extract resume facts into EvidenceStore."""

from __future__ import annotations

import re

from src.models import EvidenceStore, Fact, FactSource, JobDescription, Resume


def _slug(text: str) -> str:
    slug = re.sub(r"[^\w\u4e00-\u9fff]+", "-", text.lower()).strip("-")
    return slug[:40] or "item"


def build_evidence_store(resume: Resume, jd: JobDescription | None = None) -> EvidenceStore:
    """Build EvidenceStore from structured resume (and optional JD keywords)."""
    store = EvidenceStore()
    idx = 0

    if resume.summary:
        idx += 1
        store.add(
            Fact(
                id=f"fact-summary-{idx}",
                text=resume.summary,
                source=FactSource.RESUME,
            )
        )

    for i, exp in enumerate(resume.experiences):
        base = f"fact-exp-{i}"
        header = f"{exp.company} {exp.title}".strip()
        if header:
            store.add(
                Fact(id=f"{base}-header", text=header, source=FactSource.RESUME)
            )
        for j, ach in enumerate(exp.achievements):
            store.add(
                Fact(
                    id=f"{base}-ach-{j}",
                    text=ach,
                    source=FactSource.RESUME,
                )
            )
        if exp.description and not exp.achievements:
            store.add(
                Fact(id=f"{base}-desc", text=exp.description, source=FactSource.RESUME)
            )

    for i, skill in enumerate(resume.skills):
        store.add(
            Fact(
                id=f"fact-skill-{_slug(skill)}-{i}",
                text=skill,
                source=FactSource.RESUME,
            )
        )

    for i, proj in enumerate(resume.projects):
        store.add(
            Fact(
                id=f"fact-proj-{i}",
                text=f"{proj.name}: {'; '.join(proj.achievements) or proj.description}",
                source=FactSource.RESUME,
            )
        )

    if not store.facts and resume.raw_text:
        store.add(
            Fact(
                id="fact-raw-0",
                text=resume.raw_text[:500],
                source=FactSource.RESUME,
            )
        )

    if jd:
        for i, kw in enumerate(jd.keywords[:20]):
            store.add(
                Fact(
                    id=f"fact-jd-kw-{i}",
                    text=kw,
                    source=FactSource.JD,
                    can_use_in_resume=False,
                )
            )
        for i, req in enumerate(jd.requirements):
            store.add(
                Fact(
                    id=f"fact-jd-req-{i}",
                    text=req.text,
                    source=FactSource.JD,
                    can_use_in_resume=False,
                )
            )

    return store
