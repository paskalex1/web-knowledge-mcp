"""Web search utilities for web-knowledge-mcp."""

from __future__ import annotations

import os
from typing import Iterable, List, Optional
from urllib.parse import urlparse

from duckduckgo_search import DDGS

from .models import SearchResult

DEFAULT_MAX_RESULTS = int(os.getenv("WEB_KNOWLEDGE_SEARCH_CANDIDATES", "30"))


def _domain_matches(url: str, allowed_domains: Optional[Iterable[str]]) -> bool:
    if not allowed_domains:
        return True
    host = urlparse(url).netloc.lower().lstrip(".")
    for domain in allowed_domains:
        normalized = domain.lower().lstrip(".")
        if host == normalized or host.endswith(f".{normalized}"):
            return True
    return False


def search_web(
    query: str,
    *,
    max_results: int = DEFAULT_MAX_RESULTS,
    allowed_domains: Optional[Iterable[str]] = None,
) -> List[SearchResult]:
    """Perform DuckDuckGo search and return structured results."""

    limit = max(1, min(max_results, DEFAULT_MAX_RESULTS))
    ddg_limit = max(limit * 2, 10)
    candidates: List[SearchResult] = []

    with DDGS(timeout=10) as ddgs:
        for item in ddgs.text(query, max_results=ddg_limit):
            url = item.get("href") or item.get("url")
            if not url:
                continue
            if not _domain_matches(url, allowed_domains):
                continue
            result = SearchResult(
                title=item.get("title"),
                url=url,
                snippet=item.get("body") or item.get("snippet"),
            )
            candidates.append(result)
            if len(candidates) >= limit:
                break

    return candidates
