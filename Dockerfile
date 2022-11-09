FROM python:3.11-slim

WORKDIR /app
COPY . /app
EXPOSE 8081
RUN apt-get update -y && apt-get install -y python3-pip && apt-get update -y && apt-get install -y curl
RUN pip3 install pipenv && pipenv install --deploy --system

ENTRYPOINT ["python3"]
CMD ["run.py"]
