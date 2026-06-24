# Dockerfile specifically for kubernetes
FROM python:3.14-slim

RUN apt update && apt install -y build-essential curl gunicorn
RUN pip install pipenv

WORKDIR /app

COPY . /app
RUN pipenv install --deploy --system

ENV GUNICORN_WORKERS=6 \
    GUNICORN_WORKER_CLASS=gthread \
    GUNICORN_THREADS=8 \
    GUNICORN_TIMEOUT=0 \
    GUNICORN_KEEP_ALIVE=2

CMD ["sh", "-c", "gunicorn -b 0.0.0.0:8080 --workers ${GUNICORN_WORKERS} --worker-class ${GUNICORN_WORKER_CLASS} --threads ${GUNICORN_THREADS} --timeout ${GUNICORN_TIMEOUT} --keep-alive ${GUNICORN_KEEP_ALIVE} app:app"]
