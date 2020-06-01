FROM python:3.8-slim

WORKDIR /app
COPY . /app
EXPOSE 8081
RUN apt-get update -y && apt-get install -y python-pip && apt-get update -y && apt-get install -y curl
RUN pip3 install pipenv && pipenv install --deploy --system

ENTRYPOINT ["python3"]
CMD ["run.py"]