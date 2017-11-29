FROM python:3.6
MAINTAINER Joseph Walton

WORKDIR /app
COPY . /app
EXPOSE 8081
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["run.py"]