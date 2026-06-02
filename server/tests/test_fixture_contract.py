"""Docs fixture curl contract — jd_text must be form string, not file upload."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.main import app

FIXTURE_RESUME = Path(__file__).resolve().parents[2] / "docs" / "fixtures" / "sample-resume.docx"
FIXTURE_JD = Path(__file__).resolve().parents[2] / "docs" / "fixtures" / "sample-jd.txt"
MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def test_readme_style_jd_file_upload_returns_422():
    client = TestClient(app)
    jd = FIXTURE_JD.read_text(encoding="utf-8")
    r = client.post(
        "/sessions",
        files={
            "resume": ("resume.docx", FIXTURE_RESUME.read_bytes(), MIME),
            "jd_text": ("sample-jd.txt", jd.encode(), "text/plain"),
        },
        data={"consent": "true"},
    )
    assert r.status_code == 422


def test_m1_form_jd_string_succeeds():
    client = TestClient(app)
    r = client.post(
        "/sessions",
        files={"resume": ("resume.docx", FIXTURE_RESUME.read_bytes(), MIME)},
        data={"jd_text": FIXTURE_JD.read_text(encoding="utf-8"), "consent": "true"},
    )
    assert r.status_code == 200
    assert "session_id" in r.json()
