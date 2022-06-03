FROM python:3.10-slim-buster

USER root
RUN useradd -u 1000 -m discord-bot

RUN apt-get -y update && apt-get install -y git

USER discord-bot

WORKDIR /app

COPY --chown=1000:1000 requirements.txt requirements.txt
COPY --chown=1000:1000 . .

USER root
RUN pip3 install -r requirements.txt

# CMD ["python3","-u","main.py"]
ENTRYPOINT ["sleep", "infinity"]