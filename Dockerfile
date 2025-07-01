FROM python:3.13-bookworm
LABEL authors="joey-hzpfywtd@hotmail.com"
WORKDIR /app

COPY . /app/
RUN python3 -m pip install --no-cache-dir --upgrade -r /app/requirements.txt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
