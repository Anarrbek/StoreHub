# Быстрый старт Project ZT

## Для Windows

1. Откройте PowerShell или CMD в папке проекта
2. Запустите скрипт:
```powershell
.\run.bat
```

## Для Linux/Mac

1. Откройте терминал в папке проекта
2. Дайте права на выполнение:
```bash
chmod +x run.sh
```

3. Запустите скрипт:
```bash
./run.sh
```

## Первый запуск (ручной способ)

```bash
# 1. Создание виртуального окружения
python -m venv venv

# 2. Активация (Windows)
venv\Scripts\activate
# или (Linux/Mac)
source venv/bin/activate

# 3. Установка зависимостей
pip install -r requirements.txt

# 4. Миграции БД
python manage.py migrate

# 5. Создание администратора (опционально)
python manage.py createsuperuser

# 6. Запуск сервера
python manage.py runserver
```

## Доступ

- **Сайт:** http://127.0.0.1:8000
- **Админпанель:** http://127.0.0.1:8000/admin
- **API (Swagger):** http://127.0.0.1:8000/api/docs

## Production

Для развёртывания на реальном сервере смотрите [DEPLOYMENT.md](DEPLOYMENT.md)

## Решение проблем

### Ошибка: "No module named 'rest_framework'"
```bash
pip install djangorestframework
```

### Ошибка БД
```bash
python manage.py migrate
```

### Нужно пересобрать статические файлы
```bash
python manage.py collectstatic --noinput
```
