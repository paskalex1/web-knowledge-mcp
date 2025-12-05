"""HTML parsing helpers."""

from __future__ import annotations

from bs4 import BeautifulSoup
from markdownify import markdownify as html_to_md
from readability import Document

from .models import ParsedDocument


NOISE_SELECTORS = [
    "nav",
    "header",
    "footer",
    "aside",
    "form",
    "script",
    "style",
]


def parse_html(raw_html: str) -> ParsedDocument:
    """Extract main content from HTML using readability + BeautifulSoup."""

    document = Document(raw_html)
    summary_html = document.summary(html_partial=True)
    title = document.short_title() or document.title()
    soup = BeautifulSoup(summary_html, "lxml")

    for selector in NOISE_SELECTORS:
        for node in soup.select(selector):
            node.decompose()

    plain_text = soup.get_text("\n", strip=True)
    markdown = html_to_md(str(soup), heading_style="ATX", strip="script|style")

    return ParsedDocument(title=title, plain_text=plain_text, markdown=markdown)
