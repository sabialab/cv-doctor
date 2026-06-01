"""DOCX resume parser — structured Resume + raw_text."""

from __future__ import annotations

import re
from io import BytesIO

from docx import Document

from src.models import ContactInfo, Education, Experience, Project, Resume

_SECTION_MARKERS = {
    "summary": ("自我评价", "个人简介", "summary", "profile"),
    "skills": ("技能", "专业技能", "skills", "技术栈"),
    "experience": ("工作经历", "工作经验", "experience", "work"),
    "education": ("教育", "education", "学历"),
    "projects": ("项目", "projects", "project"),
}


def _detect_section(line: str) -> str | None:
    lower = line.lower().strip()
    for section, markers in _SECTION_MARKERS.items():
        for marker in markers:
            if marker.lower() in lower and len(line) < 30:
                return section
    return None


def _parse_contact(lines: list[str]) -> ContactInfo:
    contact = ContactInfo()
    joined = " ".join(lines[:8])
    if email := re.search(r"[\w.+-]+@[\w.-]+\.\w+", joined):
        contact.email = email.group(0)
    if phone := re.search(r"1[3-9]\d{9}", joined):
        contact.phone = phone.group(0)
    return contact


def _parse_bullets(lines: list[str]) -> list[str]:
    bullets: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("-", "•", "·", "*")) or re.match(r"^\d+[.)]\s", stripped):
            bullets.append(re.sub(r"^[-•·*\d.)]+\s*", "", stripped))
        elif stripped:
            bullets.append(stripped)
    return bullets


def parse_resume(docx_bytes: bytes) -> Resume:
    """Parse DOCX bytes into Resume with raw_text fallback."""
    doc = Document(BytesIO(docx_bytes))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    raw_text = "\n".join(paragraphs)

    if not paragraphs:
        return Resume(name="未知", raw_text=raw_text)

    name = paragraphs[0]
    contact = _parse_contact(paragraphs)

    summary = ""
    skills: list[str] = []
    experiences: list[Experience] = []
    education: list[Education] = []
    projects: list[Project] = []

    current_section: str | None = None
    section_lines: list[str] = []

    def flush_section() -> None:
        nonlocal summary, skills, experiences, education, projects, section_lines, current_section
        if not current_section or not section_lines:
            section_lines = []
            return

        if current_section == "summary":
            summary = " ".join(section_lines)
        elif current_section == "skills":
            joined = " ".join(section_lines)
            skills = [s.strip() for s in re.split(r"[,，、/|]", joined) if s.strip()]
        elif current_section == "experience":
            title_line = section_lines[0]
            rest = section_lines[1:]
            company, title = title_line, ""
            if " | " in title_line:
                company, title = title_line.split(" | ", 1)
            elif " - " in title_line:
                company, title = title_line.split(" - ", 1)
            experiences.append(
                Experience(
                    company=company.strip(),
                    title=title.strip(),
                    achievements=_parse_bullets(rest),
                    description=" ".join(rest[:2]),
                )
            )
        elif current_section == "education":
            education.append(
                Education(
                    school=section_lines[0],
                    degree=section_lines[1] if len(section_lines) > 1 else "",
                )
            )
        elif current_section == "projects":
            projects.append(
                Project(
                    name=section_lines[0],
                    achievements=_parse_bullets(section_lines[1:]),
                )
            )

        section_lines = []

    for line in paragraphs[1:]:
        detected = _detect_section(line)
        if detected:
            flush_section()
            current_section = detected
            continue
        section_lines.append(line)

    flush_section()

    if not skills:
        skill_match = re.search(r"(?:技能|Skills?)[:：]\s*(.+)", raw_text, re.I)
        if skill_match:
            skills = [s.strip() for s in re.split(r"[,，、/|]", skill_match.group(1)) if s.strip()]

    return Resume(
        name=name,
        contact=contact,
        summary=summary,
        experiences=experiences,
        education=education,
        skills=skills,
        projects=projects,
        raw_text=raw_text,
    )
