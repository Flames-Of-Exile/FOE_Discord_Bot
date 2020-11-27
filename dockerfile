FROM python:3.8.0-alpine

RUN addgroup -S app && adduser -S app -G app

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

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

RUN chmod 700 /usr/src/app/entrypoint.sh

COPY . /usr/src/app/

RUN chown -R app:app /usr/src/app/

USER app

ENTRYPOINT ["sh", "/usr/src/app/entrypoint.sh"]

CMD ["python", "discordbot.py"]