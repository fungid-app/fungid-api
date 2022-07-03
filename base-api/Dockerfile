FROM python:3.9-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /base-api

COPY base-api/requirements.txt /base-api/

RUN pip install -r requirements.txt

COPY ./base-api /base-api

