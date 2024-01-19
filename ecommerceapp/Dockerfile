FROM python:3.11 AS builder

RUN apt-get update && apt-get -y install python3-pip --fix-missing

WORKDIR /app
COPY requirements.txt /app/

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY . /app/

ENV DJANGO_SETTINGS_MODULE=ecommerceapp.settings
ENV DATABASE_URL=sqlite:///ecommerceapp.sqlite3

RUN python manage.py migrate

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
