# Dockerfile specifically for kubernetes
FROM python:3.6-slim

RUN apt update && apt install -y build-essential curl gunicorn
RUN pip install pipenv

WORKDIR /app

COPY . /app
RUN pipenv install --deploy --system

EXPOSE 8082
CMD ["gunicorn", "-b", "0.0.0.0:80", "--workers 8", "--worker-class gevent", "--worker-connections 1000", "--timeout 30", "--keep-alive 2", "app:app"]

