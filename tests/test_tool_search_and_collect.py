from __future__ import annotations

from datetime import datetime, timezone

from web_knowledge_mcp import fetch, html_parser, normalize, search
from web_knowledge_mcp.models import (
    FetchResult,
    ParsedDocument,
    SearchAndCollectArgs,
    SearchResult,
)
from web_knowledge_mcp.server import search_and_collect_tool


def test_tool_collects_documents(monkeypatch):
    search_results = [
        SearchResult(title="Doc", url="https://docs.example.com/page", snippet="snippet")
    ]

    monkeypatch.setattr(search, "search_web", lambda *args, **kwargs: search_results)

    fetch_result = FetchResult(
        status="ok",
        url="https://docs.example.com/page",
        final_url="https://docs.example.com/page",
        fetched_at=datetime.now(timezone.utc),
        content_type="text/html",
        size_bytes=123,
        text="<h1>Hello</h1><p>Django ORM text.</p>",
        binary=None,
        encoding="utf-8",
    )
    monkeypatch.setattr(fetch, "fetch_url", lambda url: fetch_result)

    monkeypatch.setattr(
        html_parser,
        "parse_html",
        lambda raw: ParsedDocument(title="Hello", plain_text="Django ORM text", markdown="# Heading"),
    )

    args = SearchAndCollectArgs(query="Django ORM", project_slug="sochi-rent", max_documents=1)
    result = search_and_collect_tool(args)

    assert result.project_slug == "sochi-rent"
    assert result.documents
    assert result.documents[0].plain_text
