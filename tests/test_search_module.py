from __future__ import annotations

from typing import Iterator, List

from web_knowledge_mcp import search
from web_knowledge_mcp.models import SearchResult


class _FakeDDGS:
    def __init__(self, responses: List[dict]):
        self._responses = responses

    def __enter__(self) -> "_FakeDDGS":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: D401
        return None

    def text(self, query: str, max_results: int) -> Iterator[dict]:
        yield from self._responses


def test_search_filters_allowed_domains(monkeypatch):
    responses = [
        {"title": "Keep", "href": "https://docs.djangoproject.com/en/5.0/orm/"},
        {"title": "Skip", "href": "https://example.com/nope"},
    ]
    monkeypatch.setattr(search, "DDGS", lambda timeout=10: _FakeDDGS(responses))

    results = search.search_web(
        "django orm",
        max_results=5,
        allowed_domains=["docs.djangoproject.com"],
    )

    assert len(results) == 1
    assert isinstance(results[0], SearchResult)
    assert "django" in results[0].url
