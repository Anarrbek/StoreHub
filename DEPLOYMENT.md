# Развёртывание StoreHub на production сервере

## Подготовка

1. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

2. **Создайте `.env` файл** (на основе `.env.example`):
```bash
cp .env.example .env
```

3. **Отредактируйте `.env`:**
- Установите надёжный `SECRET_KEY`
- Укажите ваш домен в `ALLOWED_HOSTS`
- Настройте параметры базы данных

## Настройка БД (PostgreSQL рекомендуется)

```bash
createdb project_zt
createuser -P postgres  # введите пароль
```

Отредактируйте `shops/settings.py` для использования PostgreSQL:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'project_zt',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Миграции

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

## Запуск с Gunicorn

```bash
gunicorn shops.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## Nginx конфигурация (пример)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 100M;

    location /static/ {
        alias /path/to/project/staticfiles/;
    }

    location /media/ {
        alias /path/to/project/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Systemd сервис (опционально)

Создайте `/etc/systemd/system/project-zt.service`:

```ini
[Unit]
Description=Project ZT Django Application
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/project
Environment="PATH=/path/to/project/venv/bin"
ExecStart=/path/to/project/venv/bin/gunicorn shops.wsgi:application --bind 127.0.0.1:8000 --workers 4
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Запуск:
```bash
sudo systemctl start project-zt
sudo systemctl enable project-zt
```

## SSL сертификат (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d your-domain.com
```

Затем отредактируйте настройки безопасности в `shops/settings.py`:
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## Проверки

- [ ] DEBUG = False в settings.py
- [ ] SECRET_KEY изменён
- [ ] ALLOWED_HOSTS настроен
- [ ] Статические файлы собраны (collectstatic)
- [ ] База данных настроена и миграции применены
- [ ] HTTPS включён (если доступен)
