FROM python:3.7-slim-buster

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .

RUN apt-get update && \
    apt-get install -y \
        libsndfile1 \
        ffmpeg && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt

COPY ./ /code
WORKDIR /code/

CMD ["bash","run_prodmode.sh"]