FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock .
RUN uv sync --no-dev --frozen
COPY . .

FROM python:3.12-slim-bookworm AS production
WORKDIR /app
RUN addgroup --system --gid 1001 app && \
    adduser --system --uid 1001 --gid 1001 app
COPY --from=builder /app /app
COPY --from=builder /app/.venv /app/.venv
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.production
RUN mkdir -p /app/staticfiles && chown -R app:app /app
EXPOSE 8000
USER app
ENTRYPOINT ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && daphne -b 0.0.0.0 -p 8000 config.asgi:application"]
