FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# SECRET_KEY falls back to a dev-only default (see settings.py) so this
# build step works with no env vars -- the real key only matters at
# runtime, set it via .env for that.
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "desktopcat_site.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
