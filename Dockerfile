FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=onlineshop.settings
ENV PYTHONPATH=/app
ENV MODE=PRODUCTION
ENV ALLOWED_HOSTS=rural-molly-laylin41-bbd1218f.koyeb.app

RUN python onlineshop/manage.py collectstatic --noinput

CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "onlineshop.wsgi:application"]