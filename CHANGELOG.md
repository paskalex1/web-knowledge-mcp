# Changelog

Все заметные изменения описываются в этом файле (формат [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/)).

## [0.1.0] — 2025-12-05

### Добавлено

- FastMCP-сервер `web-knowledge-mcp` с инструментом `search_and_collect_knowledge`.
- Модули поиска (DuckDuckGo), загрузки и нормализации HTML/PDF в Markdown.
- Pydantic-схемы `SearchAndCollectArgs` и `DocumentPayload`.
- Докер-окружение (`Dockerfile`, `docker-compose.yml`) и pyproject с зависимостями.
- Pytest-наборы для поиска, HTML/PDF парсеров и e2e проверок инструмента.
- Документация: README с описанием API и переменных окружения.
