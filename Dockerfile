FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_PREFERENCE=only-system

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project --no-cache


FROM python:3.14-slim

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app app

COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --chown=app:app main.py ./
COPY --chown=app:app lol_widget/ ./lol_widget/

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

USER app

STOPSIGNAL SIGINT

CMD ["python", "main.py"]
