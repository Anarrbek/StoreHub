@echo off
REM Скрипт для подготовки StoreHub к production (Windows)

echo.
echo 🚀 StoreHub - Production Setup Script (Windows)
echo ================================================

REM 1. Проверка Python
echo ✓ Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не установлен!
    pause
    exit /b 1
)

REM 2. Создание виртуального окружения
echo ✓ Создание виртуального окружения...
if not exist ".venv\" (
    python -m venv .venv
) else (
    echo   (уже существует)
)

REM 3. Активация
echo ✓ Активируем окружение...
call .venv\Scripts\activate.bat

REM 4. Обновление pip
echo ✓ Обновляем pip...
python -m pip install --upgrade pip

REM 5. Установка зависимостей
echo ✓ Установка зависимостей...
pip install -r requirements.txt

REM 6. Создание .env файла
if not exist ".env" (
    echo ✓ Создание .env файла...
    copy .env.example .env
    echo ⚠️  Отредактируйте .env файл перед запуском!
)

REM 7. Миграции
echo ✓ Применяем миграции БД...
python manage.py migrate

REM 8. Статические файлы
echo ✓ Собираем статические файлы...
python manage.py collectstatic --noinput

REM 9. Создание суперпользователя
echo ✓ Создаем суперпользователя...
python manage.py createsuperuser

echo.
echo ✅ Setup завершен!
echo 📍 Запустите: python manage.py runserver
echo 🔗 Откройте: http://localhost:8000
echo 👨‍💼 Админ-панель: http://localhost:8000/admin
echo.
pause
