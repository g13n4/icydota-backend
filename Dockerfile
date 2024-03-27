FROM python:3.11.8-alpine3.19
LABEL authors="joey-hzpfywtd@hotmail.com"
WORKDIR /app

COPY . /app/
RUN \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev && \
    python3 -m pip install --no-cache-dir --upgrade -r /app/requirements.txt && \
    apk --purge del .build-deps

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
