FROM python:3.4
WORKDIR /app
COPY . /app
EXPOSE 8081
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["run.py"]