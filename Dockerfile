FROM python:3.7.3-alpine3.10 AS base

RUN pip install -U pip

# Build Stage
FROM base AS build

RUN apk update && apk add build-base gcc musl-dev python3-dev libffi-dev openssl-dev

WORKDIR /wheels
COPY requirements.txt .

RUN pip wheel -r requirements.txt

# Execution Stage
FROM base

ENV PYTHONUNBUFFERED=1

COPY --from=build /wheels /wheels

RUN pip install -r /wheels/requirements.txt -f /wheels && \
    rm -rf /wheels && \
    rm -rf /root/.cache/pip/*

WORKDIR /app

COPY hoxy.py hoxy.py

ENTRYPOINT ["python"]
CMD ["hoxy.py"]
