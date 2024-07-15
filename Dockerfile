FROM python:3.12-alpine3.20
LABEL maintainer="info@noq.nu"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
COPY ./noq_django /backend
COPY ./scripts /scripts

WORKDIR /backend
EXPOSE 8000

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-deps \
        build-base postgresql-dev musl-dev linux-headers && \
    /py/bin/pip install -r /requirements.txt && \
    adduser --disabled-password --no-create-home app && \
    mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/frontend && \
    chown -R app:app /vol && \
    chmod -R 755 /vol && \
    chmod -R +x /scripts && \
    touch /backend/backend/scripts/fake_credentials.txt && \
    chown app:app /backend/backend/scripts/fake_credentials.txt

ENV PATH="/scripts:/py/bin:$PATH"

USER app

CMD ["run.sh"]