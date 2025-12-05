"""Normalization utilities for collected documents."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse

from langdetect import DetectorFactory, LangDetectException, detect

from .models import NormalizedDocument, ParsedDocument

DetectorFactory.seed = 0


def _detect_language(text: str, preferred: Optional[List[str]] = None) -> Optional[str]:
    if not text:
        return None
    try:
        detected = detect(text)
    except LangDetectException:
        return preferred[0] if preferred else None
    if preferred and detected not in preferred and preferred[0]:
        # keep detected but ensure preferred languages win if ambiguous
        return preferred[0] if detected not in preferred else detected
    return detected


def _compute_hash(text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()
    return f"sha256:{digest}"


def _suggest_tags(query: str, domain: str) -> List[str]:
    tokens = re.findall(r"[\w-]+", query.lower())
    unique_tokens = [token for token in tokens if len(token) > 2]
    tags = list(dict.fromkeys(unique_tokens))
    if domain:
        tags.append(domain.split(":")[0])
    return tags[:10]


def normalize_document(
    parsed: ParsedDocument,
    *,
    query: str,
    source_url: str,
    content_type: Optional[str],
    fetched_at: datetime,
    size_bytes: Optional[int],
    language_priority: Optional[List[str]] = None,
) -> NormalizedDocument:
    plain_text = (parsed.plain_text or "").strip()
    markdown = parsed.markdown.strip() if parsed.markdown else None
    language = _detect_language(plain_text, language_priority)
    hash_value = _compute_hash(plain_text)
    domain = urlparse(source_url).netloc.lower()
    metadata: Dict[str, str | int | None] = {
        "fetched_at": fetched_at.isoformat(),
        "content_type": content_type,
        "size_bytes": size_bytes,
        "source_domain": domain,
    }
    tags = _suggest_tags(query, domain)
    return NormalizedDocument(
        title=parsed.title,
        markdown=markdown,
        plain_text=plain_text,
        language=language,
        hash=hash_value,
        tags=tags,
        metadata=metadata,
    )
