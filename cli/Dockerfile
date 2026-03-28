FROM python:3.14-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-install-project

COPY src/ src/
RUN uv sync --frozen --no-dev


FROM base AS test

RUN uv sync --frozen
COPY tests/ tests/
RUN uv run pytest tests/ -v --tb=short


FROM python:3.14-slim AS production

WORKDIR /app
COPY --from=base /app /app
RUN ln -s /app/.venv/bin/workouter-cli /usr/local/bin/workouter-cli

ENTRYPOINT ["workouter-cli"]
CMD ["--help"]
