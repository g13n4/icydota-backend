FROM python:3.13-slim-bookworm
LABEL authors="joey-hzpfywtd@hotmail.com"
WORKDIR /app

RUN mkdir -p /app/.venv

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY . /app/

RUN mkdir -p /app/logs && mkdir -p /app/logs/workers && mkdir -p /app/logs/tasks
