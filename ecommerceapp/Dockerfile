FROM python:3.11.7-alpine3.19

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1

RUN apk update && apk add python3-dev gcc libc-dev musl-dev libffi-dev openssl-dev

WORKDIR /app

ENV DJANGO_SETTINGS_MODULE=ecommerceapp.settings
ENV DATABASE_URL=sqlite:///ecommerceapp.sqlite3

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY .env /app/docker

COPY . .
