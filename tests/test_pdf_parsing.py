from __future__ import annotations

from fpdf import FPDF

from web_knowledge_mcp import pdf_parser


def _make_pdf(text: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    output = pdf.output(dest="S")
    if isinstance(output, (bytes, bytearray)):
        return bytes(output)
    return output.encode("latin-1")


def test_pdf_parser_extracts_text():
    pdf_bytes = _make_pdf("Hello Django ORM")

    parsed = pdf_parser.parse_pdf(pdf_bytes)

    assert "Django" in parsed.plain_text
