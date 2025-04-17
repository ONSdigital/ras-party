# Dockerfile specifically for kubernetes
FROM python:3.12-slim

RUN apt update && apt install -y build-essential curl gunicorn
RUN pip install pipenv

WORKDIR /app

COPY . /app
RUN pipenv install --deploy --system

CMD ["gunicorn", "-b", "0.0.0.0:8080", "--workers", "6", "--worker-class", "gthread", "--threads", "5", "--worker-connections" ,"1000", "--timeout", "0", "--keep-alive", "2", "app:app"]
