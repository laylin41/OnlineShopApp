FROM python:3.13-slim

WORKDIR /app/onlineshop

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY onlineshop/ .

ENV DJANGO_SETTINGS_MODULE=onlineshop.settings
ENV PYTHONPATH=/app:/app/onlineshop
ENV MODE=PRODUCTION
ENV ALLOWED_HOSTS=rural-molly-laylin41-bbd1218f.koyeb.app

RUN python manage.py collectstatic --noinput

CMD gunicorn onlineshop.wsgi:application --bind 0.0.0.0:8000