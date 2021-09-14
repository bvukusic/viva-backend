#!/bin/bash

python manage.py collectstatic --noinput

python manage.py makemigrations --merge --noinput

python manage.py migrate

python manage.py runserver 0.0.0.0:8000