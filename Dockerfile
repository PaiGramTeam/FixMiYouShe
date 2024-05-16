FROM python:3.12-slim
LABEL authors="xtaodada"

WORKDIR /usr/app

COPY requirements.txt .
RUN /bin/sh -c set -eux; apt-get update; apt-get install -y --no-install-recommends git ; rm -rf /var/lib/apt/lists/* # buildkit
RUN pip install -r requirements.txt

COPY . .
CMD [ "python", "main.py" ]
