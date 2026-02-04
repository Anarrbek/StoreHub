#!/bin/bash
# Скрипт для подготовки StoreHub к production

echo "🚀 StoreHub - Production Setup Script"
echo "======================================"

# 1. Проверка Python
echo "✓ Проверка Python..."
python --version || python3 --version

# 2. Создание виртуального окружения
echo "✓ Создание виртуального окружения..."
python -m venv .venv 2>/dev/null || python3 -m venv .venv

# 3. Активация
echo "✓ Активируем окружение..."
source .venv/bin/activate

# 4. Обновление pip
echo "✓ Обновляем pip..."
pip install --upgrade pip

# 5. Установка зависимостей
echo "✓ Установка зависимостей..."
pip install -r requirements.txt

# 6. Создание .env файла
if [ ! -f .env ]; then
    echo "✓ Создание .env файла..."
    cp .env.example .env
    echo "⚠️  Отредактируйте .env файл!"
fi

# 7. Миграции
echo "✓ Применяем миграции БД..."
python manage.py migrate

# 8. Статические файлы
echo "✓ Собираем статические файлы..."
python manage.py collectstatic --noinput

# 9. Создание суперпользователя
echo "✓ Создаем суперпользователя..."
python manage.py createsuperuser

echo ""
echo "✅ Setup завершен!"
echo "📍 Запустите: python manage.py runserver"
echo "🔗 Откройте: http://localhost:8000"
echo "👨‍💼 Админ-панель: http://localhost:8000/admin"
