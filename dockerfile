FROM python:3.9.1-slim-buster

RUN useradd -ms /bin/bash app

WORKDIR /usr/src/app

RUN apt-get -y update \
    && apt-get -y install \
    gcc \
    netcat

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
