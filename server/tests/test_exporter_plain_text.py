"""Export helpers for text-only resume sessions."""

from src.services.exporter_docx import build_docx_from_plain_text


def test_build_docx_from_plain_text_non_empty():
    data = build_docx_from_plain_text("负责后端 API 设计与开发。\n熟悉 Python。")
    assert data.startswith(b"PK")
    assert len(data) > 1000
