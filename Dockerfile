FROM python:3.7-slim

ARG env='development'

ENV FLASK_ENV=$env

COPY ./ /app
WORKDIR /app

RUN apt-get update && apt-get install -y git curl
RUN pip install -r ./tests/requirements.txt;

EXPOSE 8085

CMD ./start.sh
