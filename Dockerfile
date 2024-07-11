FROM python:3.12.4-bookworm

COPY ./requirements.txt /backend/requirements.txt
COPY ./noq_django /backend

WORKDIR /backend
EXPOSE 8000

#RUN python -m venv /py
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN adduser --disabled-password -no-create-home backend

#ENV PATH="/py/bin:$PATH"

USER backend
