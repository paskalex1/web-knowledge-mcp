# Web Knowledge MCP

FastMCP-сервис, который выполняет веб-поиск, скачивает найденные документы (HTML/PDF), нормализует их в Markdown/Plain text и отдаёт готовый JSON для последующей индексации RAG Librarian в Command Center.

> **Основное применение:** агент Document Collector вызывает инструмент `search_and_collect_knowledge`, файлы автоматически сохраняются в `docs/<project>/web_knowledge/`, после чего Command Center запускает `ingest_project_docs` и свежие знания тут же доступны всем агентам.

## Возможности

- DuckDuckGo поиск с фильтрацией по доменам и языкам (легко расширяется под другие поисковики).
- Загрузка HTML/PDF, извлечение текста и конвертация в Markdown.
- Автоматическое определение языка, подсчёт хэшей и присвоение тегов.
- Унифицированный ответ:

```jsonc
{
  "project_slug": "sochi-rent-cc",
  "query": "django documentation",
  "documents": [
    {
      "source_url": "https://docs.djangoproject.com/en/stable/",
      "title": "Django documentation | Django",
      "plain_text": "...",
      "markdown": "...",
      "hash": "1e0b8c4d...",
      "language": "en",
      "tags": ["django", "docs"],
      "metadata": {
        "search_snippet": "The official Django documentation…",
        "content_type": "text/html",
        "fetched_at": "2025-12-05T08:00:01Z"
      }
    }
  ]
}
```

## Переменные окружения

| Имя | Значение | По умолчанию |
| --- | --- | --- |
| `WEB_KNOWLEDGE_PORT` | порт FastMCP | `8000` |
| `WEB_KNOWLEDGE_MAX_URLS` | ограничение URL за один вызов (search results) | `20` |
| `WEB_KNOWLEDGE_SEARCH_CANDIDATES` | сколько результатов брать до фильтрации | `30` |
| `WEB_KNOWLEDGE_MAX_BYTES` | максимальный размер скачиваемого ответа | `5_242_880` |
| `WEB_KNOWLEDGE_HTTP_TIMEOUT` | таймаут HTTP-запросов (сек.) | `15` |
| `WEB_KNOWLEDGE_USER_AGENT` | user-agent скачивателя | `web-knowledge-mcp/<version>` |
| `SERPAPI_KEY` | (опционально) ключ SerpAPI, если нужно перейти с DuckDuckGo | — |

## Быстрый старт

```bash
git clone https://github.com/paskalex1/web-knowledge-mcp.git
cd web-knowledge-mcp
docker compose up --build web-knowledge-mcp
```

После запуска зарегистрируйте MCP-сервер в Command Center (slug `web-knowledge-mcp`, base URL `http://web-knowledge-mcp:8000/mcp`) и выполните синхронизацию инструментов. Все активные агенты автоматически получат доступ к `search_and_collect_knowledge`.

## Локальная разработка без Docker

```bash
uv venv  # или python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m web_knowledge_mcp.server
```

Сервер слушает `0.0.0.0:<WEB_KNOWLEDGE_PORT>` и совместим с любым клиентом FastMCP.

## Тесты

```bash
uv pip install -e ".[test]"  # или pip install -r requirements-dev.txt
pytest
```

Тесты покрывают поиск, парсинг HTML/PDF и end-to-end обработку инструмента.

## Публикация знаний в Command Center

1. Document Collector вызывает инструмент с аргументами:

```json
{
  "query": "django tutorial pdf",
  "max_documents": 5,
  "allowed_domains": ["djangoproject.com"],
  "language_priority": ["ru", "en"]
}
```

2. Ответ сохраняется в `docs/<project>/web_knowledge/`, создаётся RAG-источник.
3. Автоматически запускается `ingest_project_docs`, Knowledge ChangeLog фиксирует diff, а RAG Librarian сообщает о новых документах.

Таким образом агенты получают свежие внешние материалы без ручного скачивания.
