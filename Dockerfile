FROM python:3.13-bookworm
LABEL authors="joey-hzpfywtd@hotmail.com"
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /app/logs && mkdir -p /app/logs/workers && mkdir -p /app/logs/tasks

COPY . /app/

