# SSL/HTTPS Setup для Production

## Варианты получения сертификата

### 1. Let's Encrypt (бесплатно, рекомендуется)

#### На Linux VPS (с Docker)

```bash
# Установить Certbot
sudo apt install certbot python3-certbot-nginx

# Получить сертификат (standalone)
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Сертификаты будут в:
# /etc/letsencrypt/live/yourdomain.com/

# Скопировать для Docker
sudo mkdir -p /path/to/project/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /path/to/project/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /path/to/project/ssl/key.pem
sudo chown -R $USER:$USER /path/to/project/ssl
```

#### На локальной машине (для тестирования)

```bash
# Установить mkcert
# Windows: choco install mkcert
# Mac: brew install mkcert
# Linux: sudo apt install mkcert

mkdir -p ssl
cd ssl

# Создать локальный CA
mkcert -install

# Создать сертификат для localhost
mkcert -cert-file=cert.pem -key-file=key.pem localhost 127.0.0.1
```

### 2. Cloudflare (с управляемым сертификатом)

```bash
# 1. Перенести домен на Cloudflare nameservers
# 2. В Cloudflare dashboard: SSL/TLS → Origin Server
# 3. Создать сертификат
# 4. Скопировать в ssl/cert.pem и ssl/key.pem
```

### 3. AWS Certificate Manager (если используете AWS)

```bash
# Через AWS console запросить сертификат
# Затем использовать с Load Balancer
```

## Конфигурация nginx.conf

Раскомментировать HTTPS секцию в `nginx.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # Безопасность
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS (принудительный HTTPS)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # ... остальная конфигурация
}

# Редирект с HTTP на HTTPS
server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}
```

## Обновление Django settings.py

Уже большинство сделано! Проверить в `shops/settings.py`:

```python
# Security Settings for HTTPS
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True') == 'True'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True') == 'True'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'True') == 'True'

# HSTS Headers
SECURE_HSTS_SECONDS = 31536000  # 1 год
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

## Запуск с SSL

### С Docker

```bash
# Обновить docker-compose.yml:
# - Убедиться что nginx слушает порт 443
# - Убедиться что ssl/ папка смонтирована в nginx контейнер

docker-compose up -d

# Проверить
curl https://localhost -k  # -k игнорирует самоподписанный сертификат
```

### Без Docker

```bash
# Обновить Django settings.py для HTTPS
# Запустить с gunicorn

gunicorn shops.wsgi:application \
  --bind 0.0.0.0:8000 \
  --certfile=ssl/cert.pem \
  --keyfile=ssl/key.pem
```

## Автоматическое обновление сертификата Let's Encrypt

```bash
# Проверить что работает
sudo certbot renew --dry-run

# Автоматическое обновление раз в месяц (Ubuntu)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# После обновления - перезагрузить nginx
sudo systemctl reload nginx
```

## Проверка SSL

### Online
- https://www.ssllabs.com/ssltest/ - анализ сертификата
- https://www.sslshopper.com/ - проверка

### Локально
```bash
openssl s_client -connect yourdomain.com:443
```

## Решение проблем

### "Certificate not trusted"
- Используется самоподписанный сертификат (нормально для dev)
- Или сертификат expired - обновить

### "Mixed content"
- HTTPS страница загружает HTTP ресурсы
- Обновить ссылки на /static/ и /media/ на HTTPS
- Или использовать относительные пути

### "Too many redirects"
- Проверить редирект с HTTP на HTTPS
- Убедиться что за nginx есть load balancer
- Обновить X-Forwarded-Proto заголовок

## Сертификат для Stripe

Если используется Stripe webhooks - нужен валидный SSL сертификат!

```bash
# Проверить что домен резолвится
nslookup yourdomain.com

# Проверить что 443 порт открыт
nmap -p 443 yourdomain.com
```

## Production Checklist

- [ ] Сертификат получен и установлен
- [ ] HTTP редирект на HTTPS работает
- [ ] HSTS включен (Strict-Transport-Security)
- [ ] Все cookies имеют Secure флаг
- [ ] CSRF cookie имеет Secure флаг
- [ ] Mixed content проверен (нет HTTP в HTTPS)
- [ ] SSL Labs оценка A+
- [ ] Renewals настроены для автоматического обновления
- [ ] Backup сертификатов сделан

## Цена

- Let's Encrypt: **БЕСПЛАТНО** ✅
- Cloudflare: **БЕСПЛАТНО** для базовой поддержки
- Digicert: от $300/год
- Comodo: от $50/год
