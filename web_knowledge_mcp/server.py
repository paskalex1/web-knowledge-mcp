"""Entrypoint for the web-knowledge-mcp server."""

from __future__ import annotations

import os
from typing import Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from . import fetch, html_parser, normalize, pdf_parser, search
from .models import (
    DocumentPayload,
    NormalizedDocument,
    ParsedDocument,
    SearchAndCollectArgs,
    SearchAndCollectResult,
)

PORT = int(os.getenv("WEB_KNOWLEDGE_PORT", "8000"))
MAX_URLS_PER_CALL = int(os.getenv("WEB_KNOWLEDGE_MAX_URLS", "20"))

mcp = FastMCP("WebKnowledgeMCP", json_response=True, host="0.0.0.0", port=PORT)


def _build_document_payload(
    doc: NormalizedDocument, *, source_url: str, extra_meta: Optional[Dict[str, str]] = None
) -> DocumentPayload:
    metadata = dict(doc.metadata)
    metadata.setdefault("source_url", source_url)
    if extra_meta:
        metadata.update(extra_meta)
    return DocumentPayload(
        source_url=source_url,
        title=doc.title,
        markdown=doc.markdown,
        plain_text=doc.plain_text,
        hash=doc.hash,
        language=doc.language,
        tags=doc.tags,
        metadata=metadata,
    )


@mcp.tool(name="search_and_collect_knowledge")
def search_and_collect_tool(payload: SearchAndCollectArgs) -> SearchAndCollectResult:
    """Search the web, fetch documents and return normalized knowledge objects."""

    candidate_limit = min(MAX_URLS_PER_CALL, max(payload.max_documents * 3, payload.max_documents))
    results = search.search_web(
        payload.query,
        max_results=candidate_limit,
        allowed_domains=payload.allowed_domains,
    )

    collected: List[DocumentPayload] = []
    for candidate in results:
        if len(collected) >= payload.max_documents:
            break
        fetch_result = fetch.fetch_url(str(candidate.url))
        if fetch_result.status != "ok":
            continue

        parsed: ParsedDocument | None = None
        if fetch_result.is_pdf and fetch_result.binary:
            parsed = pdf_parser.parse_pdf(fetch_result.binary)
        elif fetch_result.text:
            parsed = html_parser.parse_html(fetch_result.text)

        if not parsed or not parsed.plain_text.strip():
            continue

        normalized_doc = normalize.normalize_document(
            parsed,
            query=payload.query,
            source_url=str(fetch_result.final_url),
            content_type=fetch_result.content_type,
            fetched_at=fetch_result.fetched_at,
            size_bytes=fetch_result.size_bytes,
            language_priority=payload.language_priority,
        )
        collected.append(
            _build_document_payload(
                normalized_doc,
                source_url=str(fetch_result.final_url),
                extra_meta={"search_snippet": candidate.snippet} if candidate.snippet else None,
            )
        )

    return SearchAndCollectResult(
        project_slug=payload.project_slug,
        query=payload.query,
        documents=collected,
    )


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
