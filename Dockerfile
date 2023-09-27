FROM python:3.11.4-alpine

COPY ./requirements.txt /requirements.txt

COPY ./pricing /pricing

RUN pip install -r requirements.txt

CMD ["python", "/app/main.py"]

EXPOSE 80