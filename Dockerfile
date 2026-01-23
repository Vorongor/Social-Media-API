FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY requirements.txt /code/

RUN pip install -r requirements.txt

COPY . /code/

RUN mkdir -p /code/media && \
    adduser --disabled-password --no-create-home django-user && \
    chown -R django-user:django-user /code && \
    chmod -R 755 /code/media

USER django-user