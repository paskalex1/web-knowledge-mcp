"""HTTP fetching helpers."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Optional

import httpx

from .models import FetchResult

MAX_BYTES = int(os.getenv("WEB_KNOWLEDGE_MAX_BYTES", 5 * 1024 * 1024))
TIMEOUT = float(os.getenv("WEB_KNOWLEDGE_HTTP_TIMEOUT", 15))
USER_AGENT = os.getenv(
    "WEB_KNOWLEDGE_USER_AGENT",
    "web-knowledge-mcp/0.1 (+https://sochi.rent/command-center)",
)


def fetch_url(url: str) -> FetchResult:
    """Download URL contents with simple safeguards."""

    headers = {"User-Agent": USER_AGENT}
    try:
        with httpx.Client(headers=headers, follow_redirects=True, timeout=TIMEOUT) as client:
            response = client.get(url)
    except httpx.RequestError as exc:
        return FetchResult(
            status="error",
            url=url,
            final_url=url,
            fetched_at=datetime.now(timezone.utc),
            content_type=None,
            size_bytes=None,
            error=str(exc),
        )

    fetched_at = datetime.now(timezone.utc)
    content_length_header = response.headers.get("content-length")
    size = len(response.content)
    if size > MAX_BYTES:
        return FetchResult(
            status="error",
            url=url,
            final_url=str(response.url),
            fetched_at=fetched_at,
            content_type=response.headers.get("content-type"),
            size_bytes=size,
            error=f"Response exceeds limit of {MAX_BYTES} bytes",
        )

    content_type = response.headers.get("content-type", "").split(";")[0].lower()
    payload: Optional[str] = None
    binary: Optional[bytes] = None
    encoding = response.encoding or "utf-8"

    if response.is_error:
        return FetchResult(
            status="error",
            url=url,
            final_url=str(response.url),
            fetched_at=fetched_at,
            content_type=content_type,
            size_bytes=size,
            error=f"HTTP {response.status_code}",
        )

    if "pdf" in content_type:
        binary = bytes(response.content)
    else:
        payload = response.text

    return FetchResult(
        status="ok",
        url=url,
        final_url=str(response.url),
        fetched_at=fetched_at,
        content_type=content_type or None,
        size_bytes=size,
        text=payload,
        binary=binary,
        encoding=encoding,
    )
