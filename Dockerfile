FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock .python-version ./

RUN uv sync --frozen --no-dev

COPY src/ ./src/
COPY configs/ ./configs/
COPY notebooks/ ./notebooks/

ENV PATH="/app/.venv/bin:$PATH"

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
