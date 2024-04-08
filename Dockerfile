FROM python:3.11.8-alpine3.19
LABEL authors="joey-hzpfywtd@hotmail.com"
WORKDIR /app

COPY . /app/
RUN python3 -m pip install --no-cache-dir --upgrade -r /app/requirements_light.txt 

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
