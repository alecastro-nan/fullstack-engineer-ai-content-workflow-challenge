FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
WORKDIR /app
COPY pyproject.toml .
RUN uv sync --no-dev --frozen
COPY . .

FROM python:3.12-slim-bookworm AS production
WORKDIR /app
RUN addgroup --system --gid 1001 app && \
    adduser --system --uid 1001 --gid 1001 app
COPY --from=builder /app /app
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production
EXPOSE 8000
USER app
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker"]
