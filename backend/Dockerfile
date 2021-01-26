FROM python:3.7-alpine

WORKDIR /app

# Flush logs immediately
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache \
  # For `psycopg2`.
  musl-dev gcc postgresql-dev \
  # For `wait-for-postgres.sh` script.
  postgresql-client \
  # For the installation of django-nopassword
  git

COPY ./requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

ENV DEBUG FALSE

COPY ./ /app

RUN python manage.py collectstatic --noinput --clear --link
CMD python manage.py migrate --noinput && gunicorn --bind 0.0.0.0:$PORT -w 4 prevencija.wsgi --error-logfile -
