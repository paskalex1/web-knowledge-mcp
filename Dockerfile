FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml /app/
COPY web_knowledge_mcp /app/web_knowledge_mcp

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["python", "-m", "web_knowledge_mcp.server"]
