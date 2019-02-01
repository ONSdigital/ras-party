FROM python:3.6-slim

WORKDIR /app
COPY . /app
EXPOSE 8081
RUN apt-get update -y && apt-get install -y python-pip && apt-get update -y && apt-get install -y curl
RUN pip3 install pipenv && pipenv install --deploy --system

CMD ["/usr/local/bin/gunicorn", "-b", "0.0.0.0:8081", "--workers", "4", "--worker-class", "gevent", "--worker-connections", "1000", "--timeout", "30", "--keep-alive", "2", "app:app"]