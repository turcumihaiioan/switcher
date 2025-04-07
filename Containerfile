FROM python:alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN apk add --no-cache git

COPY ./app /code/app

CMD ["fastapi", "run", "app/main.py"]
