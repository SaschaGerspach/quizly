FROM python:3

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg git curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

COPY . .

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD sh -c "python manage.py migrate --noinput && \
           gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3"
