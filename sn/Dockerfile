FROM python:3.8-alpine

WORKDIR /sn

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

COPY ./requirements.txt /sn/requirements.txt

RUN set -eux \
    && apk add --no-cache --virtual .build-deps build-base \
       libressl-dev libffi-dev gcc musl-dev python3-dev \
       libc-dev libxslt-dev libxml2-dev bash \
       postgresql-dev \
    && pip install --upgrade pip setuptools wheel \
    && pip install -r /sn/requirements.txt \
    && rm -rf /root/.cache/pip

COPY . /sn