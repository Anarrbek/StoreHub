FROM python:3.13-slim

WORKDIR /app

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn psycopg2-binary redis django-cors-headers

# Копирование кода приложения
COPY . .

# Создание директорий для логов
RUN mkdir -p logs

# Сборка статических файлов
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "shops.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
