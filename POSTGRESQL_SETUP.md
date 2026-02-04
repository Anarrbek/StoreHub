# PostgreSQL Setup для Production

## Установка PostgreSQL

### Windows
```bash
# Скачать установщик с https://www.postgresql.org/download/windows/
# или через Chocolatey:
choco install postgresql

# По умолчанию:
# User: postgres
# Port: 5432
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### macOS
```bash
brew install postgresql
brew services start postgresql
```

## Создание БД и юзера

```bash
# Войти в PostgreSQL
psql -U postgres

# В PostgreSQL shell:
CREATE DATABASE storehub;
CREATE USER storehub_user WITH PASSWORD 'YOUR_SECURE_PASSWORD_HERE';

ALTER ROLE storehub_user SET client_encoding TO 'utf8';
ALTER ROLE storehub_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE storehub_user SET default_transaction_deferrable TO on;
ALTER ROLE storehub_user SET default_transaction_level TO 'read committed';

GRANT ALL PRIVILEGES ON DATABASE storehub TO storehub_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO storehub_user;

\q
```

## Обновление settings.py

Уже сделано! В settings.py используется переменная окружения:

```python
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    import dj_database_url
    DATABASES['default'] = dj_database_url.config(default=DATABASE_URL)
```

## Обновление .env

Добавить в `.env`:
```
DATABASE_URL=postgresql://storehub_user:YOUR_PASSWORD@localhost:5432/storehub
```

## Миграция данных

```bash
# Активировать venv
. venv/Scripts/activate  # Windows
source venv/bin/activate  # Linux/Mac

# Установить dj-database-url если нет
pip install dj-database-url

# Выполнить миграции
python manage.py migrate

# Создать супер-пользователя
python manage.py createsuperuser

# Запустить сервер
python manage.py runserver
```

## Backup и Restore

### Backup
```bash
pg_dump -U storehub_user -h localhost storehub > backup.sql
```

### Restore
```bash
psql -U storehub_user -h localhost storehub < backup.sql
```

## Оптимизация для Production

Добавить в `/etc/postgresql/13/main/postgresql.conf`:
```
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 1310kB
min_wal_size = 1GB
max_wal_size = 4GB
```

Затем перезагрузить:
```bash
sudo systemctl restart postgresql
```

## Проверка соединения

```bash
psql -U storehub_user -h localhost -d storehub
```

Если успешно подключилась - всё готово! ✅
