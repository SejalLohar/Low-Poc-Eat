FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev gcc pkg-config && \
    apt-get clean




COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && gunicorn DjangoProject2.wsgi:application --bind 0.0.0.0:8000"]

RUN mkdir -p /app/staticfiles

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev gcc pkg-config netcat-openbsd && \
    apt-get clean

