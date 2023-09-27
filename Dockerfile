FROM python:3.11.4-alpine

COPY ./requirements.txt /requirements.txt

COPY ./pricing /pricing

RUN pip install -r requirements.txt

CMD ["python", "/pricing/main.py"]

EXPOSE 80