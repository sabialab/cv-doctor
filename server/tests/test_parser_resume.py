"""Resume parser tests."""

from __future__ import annotations

from pathlib import Path

from src.parser_resume import parse_resume

FIXTURE = Path(__file__).resolve().parents[2] / "docs" / "fixtures" / "sample-resume.docx"


def test_parse_sample_resume_fixture():
    assert FIXTURE.is_file(), f"missing fixture: {FIXTURE}"
    resume = parse_resume(FIXTURE.read_bytes())
    assert resume.name == "张明"
    assert resume.raw_text
    assert "Python" in resume.raw_text
    assert len(resume.experiences) >= 1
    assert any("Python" in s for s in resume.skills) or "Python" in resume.raw_text


def test_parse_empty_docx():
    from io import BytesIO

    from docx import Document

    buf = BytesIO()
    Document().save(buf)
    resume = parse_resume(buf.getvalue())
    assert resume.name == "未知"
    assert resume.raw_text == ""
