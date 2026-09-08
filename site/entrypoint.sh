#!/bin/sh
# Runs migrations before gunicorn starts. There's no separate deploy
# pipeline for this site, so this is the only place migrations run --
# once, synchronously, before gunicorn forks its worker processes.
set -e

python manage.py migrate --noinput

exec gunicorn desktopcat_site.wsgi:application --bind 0.0.0.0:8000 --workers 3
