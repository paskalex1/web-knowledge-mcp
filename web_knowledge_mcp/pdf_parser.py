"""PDF parsing helpers."""

from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader

from .models import ParsedDocument


def parse_pdf(content: bytes) -> ParsedDocument:
    """Extract text from PDF bytes using PyPDF."""

    reader = PdfReader(BytesIO(content))
    texts = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        texts.append(page_text.strip())
    plain_text = "\n\n".join(filter(None, texts)).strip()
    return ParsedDocument(title=None, plain_text=plain_text, markdown=None)
