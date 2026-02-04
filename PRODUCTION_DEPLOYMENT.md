# StoreHub - Полное руководство по развертыванию в production

## 📋 Оглавление
1. [Требования](#требования)
2. [Локальная установка](#локальная-установка)
3. [Docker развертывание](#docker-развертывание)
4. [Облачное развертывание](#облачное-развертывание)
5. [Настройка Stripe](#настройка-stripe)
6. [Настройка Email](#настройка-email)
7. [Безопасность](#безопасность)
8. [Мониторинг](#мониторинг)

## Требования

- Python 3.13+
- PostgreSQL 13+
- Redis 6+
- Nginx
- SSL сертификат (Let's Encrypt)
- Stripe аккаунт
- SMTP сервер для email

## Локальная установка

### 1. Клонирование и окружение

```bash
git clone <repository-url>
cd PrjectZT

# Создание virtual environment
python -m venv .venv

# Linux/Mac
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Конфигурация

```bash
# Копирование .env файла
cp .env.production .env

# Редактирование .env с вашими параметрами
nano .env
```

### 3. Инициализация БД

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 4. Запуск

```bash
python manage.py runserver
```

## Docker развертывание

### 1. Подготовка

```bash
# Создание .env файла
cp .env.production .env
# Редактируйте .env с вашими значениями
```

### 2. Запуск контейнеров

```bash
docker-compose up -d

# Инициализация БД
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### 3. Проверка

```bash
# Логи
docker-compose logs -f web

# Статус контейнеров
docker-compose ps
```

## Облачное развертывание

### Вариант 1: Heroku

```bash
# Инициализация Heroku
heroku login
heroku create storehouse-app
heroku addons:create heroku-postgresql:standard-0
heroku addons:create heroku-redis:premium-0

# Установка переменных окружения
heroku config:set DEBUG=False
heroku config:set DJANGO_SECRET_KEY=your-secret-key
heroku config:set STRIPE_PUBLIC_KEY=pk_live_...
heroku config:set STRIPE_SECRET_KEY=sk_live_...

# Развертывание
git push heroku main
heroku run python manage.py migrate
```

### Вариант 2: Digital Ocean

```bash
# Создание Droplet с Ubuntu 22.04

# 1. Обновление системы
sudo apt update && sudo apt upgrade -y

# 2. Установка зависимостей
sudo apt install -y python3.13 python3-pip python3-venv \
  postgresql postgresql-contrib redis-server nginx git

# 3. Клонирование репозитория
cd /opt
sudo git clone <repository-url>
cd PrjectZT

# 4. Создание окружения
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Конфигурация PostgreSQL
sudo -u postgres createdb storehouse
sudo -u postgres createuser storehouse_user
sudo -u postgres psql -c "ALTER USER storehouse_user WITH PASSWORD 'password';"

# 6. Миграции
python manage.py migrate
python manage.py collectstatic --noinput

# 7. Systemd сервис (в /etc/systemd/system/storehouse.service)
[Unit]
Description=StoreHub Django Application
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/PrjectZT
ExecStart=/opt/PrjectZT/venv/bin/gunicorn shops.wsgi:application --bind 127.0.0.1:8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# 8. Запуск сервиса
sudo systemctl daemon-reload
sudo systemctl start storehouse
sudo systemctl enable storehouse

# 9. Nginx конфиг (/etc/nginx/sites-available/storehouse)
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /opt/PrjectZT/staticfiles/;
    }

    location /media/ {
        alias /opt/PrjectZT/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}

# 10. Активация Nginx
sudo ln -s /etc/nginx/sites-available/storehouse /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 11. SSL сертификат (Let's Encrypt)
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### Вариант 3: AWS

```bash
# Используйте Elastic Beanstalk для простого развертывания
eb init -p python-3.13 storehouse
eb create production
eb deploy
```

## Настройка Stripe

### 1. Получение ключей

1. Зарегистрируйтесь на [stripe.com](https://stripe.com)
2. Перейдите в Dashboard → API Keys
3. Скопируйте Publishable Key и Secret Key

### 2. Конфигурация

```bash
# В .env файле
STRIPE_PUBLIC_KEY=pk_live_your_key
STRIPE_SECRET_KEY=sk_live_your_secret
```

### 3. Использование в коде

```python
# Примеры в payment_views.py уже готовы
# Использование:
POST /api/v1/create-payment-intent/ 
```

## Настройка Email

### Gmail SMTP

```bash
# 1. Включить 2FA в аккаунте Google
# 2. Создать App Password на https://myaccount.google.com/apppasswords

# В .env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### SendGrid

```bash
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
SENDGRID_API_KEY=your-sendgrid-key
```

## Безопасность

### Обязательные действия

1. **Смена SECRET_KEY**
   ```python
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```

2. **HTTPS**
   - Получить SSL сертификат от Let's Encrypt
   - Установить `SECURE_SSL_REDIRECT=True`

3. **Пароли БД**
   - Использовать сильные пароли
   - Хранить в переменных окружения

4. **CSRF Protection**
   - `CSRF_COOKIE_SECURE=True`
   - `SESSION_COOKIE_SECURE=True`

5. **Headers Security**
   - `X_FRAME_OPTIONS='DENY'`
   - `SECURE_HSTS_SECONDS=31536000`

### Регулярные проверки

```bash
# Проверка безопасности
python manage.py check --deploy

# Обновление зависимостей
pip list --outdated
pip install --upgrade pip setuptools wheel
```

## Мониторинг

### Логирование

```bash
# Проверка логов
tail -f logs/django.log

# С использованием ELK Stack
# docker run -d -p 5601:5601 docker.elastic.co/kibana/kibana:8.0.0
```

### Метрики производительности

```bash
# Использование Django Debug Toolbar в development
pip install django-debug-toolbar

# Production monitoring с NewRelic
pip install newrelic
```

### Резервные копии

```bash
# PostgreSQL резервная копия
pg_dump -U storehouse_user -h localhost storehouse > backup.sql

# Восстановление
psql -U storehouse_user -h localhost storehouse < backup.sql

# Media файлы
tar -czf media_backup.tar.gz media/
```

## Масштабирование

### Кэширование

```python
# Redis кэширование
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### CDN

```python
# AWS CloudFront для статических файлов
STATIC_URL = 'https://d123.cloudfront.net/static/'
```

### Очередь задач (Celery)

```python
# Долгие операции в фоне
from celery import shared_task

@shared_task
def send_notification_email(user_id):
    # отправка email...
    pass
```

## Контакты поддержки

Email: support@storehouse.com
Документация: https://docs.storehouse.com

---

**Версия документации:** 1.0  
**Последнее обновление:** January 2026
