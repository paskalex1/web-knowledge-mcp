from __future__ import annotations

from pathlib import Path

from web_knowledge_mcp import html_parser

BASE = Path(__file__).parent / "data"


def test_html_parser_extracts_main_text():
    sample_html = (BASE / "sample.html").read_text(encoding="utf-8")

    parsed = html_parser.parse_html(sample_html)

    assert "Django ORM" in parsed.plain_text
    assert parsed.markdown is not None
    assert parsed.title.lower().startswith("sample")
