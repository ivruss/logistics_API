FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip
# Установка poetry
RUN python -m pip install --no-cache-dir poetry

RUN mkdir -p /home/api

WORKDIR /home/api

# Копирование файлов с зависимостями
COPY ./requirements.txt .

# Установка зависимостей
RUN pip install -r requirements.txt

# Копирование файлов приложения
COPY ./api .


