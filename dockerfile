FROM python:3.8.0-alpine

WORKDIR /usr/src/app

RUN apk update \
    && apk add \
    gcc \
    musl-dev \
    python3-dev

RUN apk update \
    && apk add --no-cache \
    bash 

RUN pip install --upgrade pip \
    && pip install --upgrade wheel
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY . /usr/src/app/

ENTRYPOINT [ "python", "discordbot.py" ]