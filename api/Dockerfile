FROM python:3.12-slim AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies (ignoring empty pyproject.toml if it was empty, but assuming uv init was run)
RUN uv sync --frozen --no-dev --no-install-project

# Copy source
COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .

# Install the project itself
RUN uv sync --frozen --no-dev

# --- Test stage ---
FROM base AS test

RUN uv sync --frozen

COPY tests/ tests/
COPY config.example.yaml config.yaml

# Run all tests — build fails if tests fail
# Using --anyio-backend=asyncio for pytest-asyncio
RUN uv run pytest tests/ -v --tb=short

# --- Production stage ---
FROM base AS production

COPY config.example.yaml config.example.yaml

RUN mkdir -p /app/data /app/backups

EXPOSE 8000

ENV PYTHONPATH=/app/src

CMD ["uv", "run", "uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
