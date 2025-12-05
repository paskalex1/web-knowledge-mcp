"""Pydantic models for the web-knowledge-mcp server."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, HttpUrl, field_validator


class SearchAndCollectArgs(BaseModel):
    """Incoming payload for search_and_collect_knowledge."""

    query: str = Field(..., min_length=3, description="Текстовый поисковый запрос")
    project_slug: Optional[str] = Field(
        default=None, description="Идентификатор проекта, для которого собираются знания"
    )
    max_documents: int = Field(
        default=10,
        ge=1,
        le=20,
        description="Максимальное количество документов в ответе",
    )
    allowed_domains: Optional[List[str]] = Field(
        default=None,
        description="Белый список доменов для фильтрации результатов",
    )
    language_priority: Optional[List[str]] = Field(
        default=None,
        description="Приоритеты языков (например ['ru','en'])",
    )

    @field_validator("allowed_domains", mode="before")
    @classmethod
    def _normalize_domains(cls, value):
        if value is None:
            return value
        return [domain.lower().lstrip(".") for domain in value if domain]


class DocumentPayload(BaseModel):
    """Готовый документ, который можно передавать в RAG."""

    source_url: HttpUrl
    title: Optional[str] = None
    markdown: Optional[str] = None
    plain_text: str = Field(..., min_length=10)
    hash: str
    language: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchAndCollectResult(BaseModel):
    project_slug: Optional[str]
    query: str
    documents: List[DocumentPayload]


class SearchResult(BaseModel):
    title: Optional[str]
    url: str
    snippet: Optional[str] = None

    @field_validator("url")
    @classmethod
    def _ensure_url(cls, value: str) -> str:
        parsed = urlparse(value)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL")
        return value

    @property
    def domain(self) -> str:
        return urlparse(self.url).netloc.lower()


class FetchResult(BaseModel):
    status: str
    url: HttpUrl
    final_url: HttpUrl
    fetched_at: datetime
    content_type: Optional[str]
    size_bytes: Optional[int]
    text: Optional[str] = None
    binary: Optional[bytes] = None
    encoding: Optional[str] = None
    error: Optional[str] = None

    @property
    def is_pdf(self) -> bool:
        return bool(self.content_type and "pdf" in self.content_type)

    @property
    def is_html(self) -> bool:
        return bool(self.content_type and "html" in self.content_type)


class ParsedDocument(BaseModel):
    title: Optional[str]
    plain_text: str
    markdown: Optional[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NormalizedDocument(BaseModel):
    title: Optional[str]
    markdown: Optional[str]
    plain_text: str
    language: Optional[str]
    hash: str
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
