# Docker & Docker Compose для Production

## Установка Docker

### Windows
```bash
# Скачать Docker Desktop с https://www.docker.com/products/docker-desktop
# Установить и перезагрузить компьютер
```

### Linux (Ubuntu)
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER
sudo systemctl start docker
sudo systemctl enable docker
```

### macOS
```bash
# Через Homebrew
brew install docker docker-compose
```

## Файлы для Docker

- `Dockerfile` - конфиг контейнера приложения
- `docker-compose.yml` - оркестрация всех сервисов
- `nginx.conf` - конфиг веб-сервера
- `.dockerignore` - исключить файлы из образа

## Запуск в Docker

### 1. Создать .env файл

```bash
cp .env.example .env
```

Обновить значения:
```env
DEBUG=False
SECRET_KEY=your-generated-secret-key
DB_PASSWORD=your-secure-password
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
```

### 2. Запустить все сервисы

```bash
docker-compose up -d
```

Будут запущены:
- **PostgreSQL** (порт 5432)
- **Redis** (порт 6379)
- **Django приложение** (порт 8000)
- **Celery worker** (фоновые задачи)
- **Nginx** (порт 80/443)

### 3. Проверка

```bash
# Логи всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f web

# Статус контейнеров
docker-compose ps
```

### 4. Создать пользователя admin

```bash
docker-compose exec web python manage.py createsuperuser
```

### 5. Доступ

- **Django**: http://localhost:8000
- **Admin панель**: http://localhost:8000/admin
- **API**: http://localhost:8000/api/

## Остановка

```bash
docker-compose down
```

Сохранит данные в volumes.

## Удаление всего

```bash
docker-compose down -v
```

⚠️ Удалит БД и все данные!

## Локальная разработка

```bash
# Выключить Celery для простоты
docker-compose up -d db redis web

# Или просто использовать локальный Django
python manage.py runserver
```

## Развертывание на сервер

### На Linux VPS

```bash
# Скачать проект
git clone <repo-url>
cd PrjectZT

# Создать .env с production переменными
nano .env

# Запустить
docker-compose -f docker-compose.yml up -d

# Настроить SSL (Let's Encrypt)
sudo certbot certonly --standalone -d yourdomain.com

# Скопировать сертификаты
sudo mkdir -p ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/key.pem
sudo chown -R 1000:1000 ssl

# Включить HTTPS в nginx.conf и перезагрузить
docker-compose restart nginx
```

## Production Checklist

- [ ] Изменить SECRET_KEY (сгенерировать новый)
- [ ] Установить DEBUG=False
- [ ] Настроить ALLOWED_HOSTS
- [ ] Установить DATABASE_URL для PostgreSQL
- [ ] Добавить Stripe ключи
- [ ] Настроить SSL сертификат
- [ ] Настроить Email отправку
- [ ] Включить SECURE_SSL_REDIRECT
- [ ] Включить SESSION_COOKIE_SECURE
- [ ] Включить CSRF_COOKIE_SECURE
- [ ] Настроить резервное копирование БД
- [ ] Установить мониторинг и логирование

## Обновление приложения

```bash
git pull origin main
docker-compose build
docker-compose up -d
```

## Масштабирование

Добавить больше workers в docker-compose.yml:

```yaml
services:
  web:
    ...
    command: gunicorn shops.wsgi:application --bind 0.0.0.0:8000 --workers 8
```

Или использовать load balancer.
