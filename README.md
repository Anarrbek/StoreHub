# StoreHub - Онлайн магазин

Лучший онлайн магазин для покупок качественных товаров с быстрыми доставками и удобным интерфейсом.

## Возможности

- ✅ Каталог товаров с пагинацией (3 колонки, 15 товаров на странице)
- ✅ Поддержка нескольких языков (Русский, Кыргызский, English)
- ✅ Система избранного
- ✅ Корзина товаров
- ✅ Заказы и оформление покупок
- ✅ Система бронирования товаров
- ✅ Отзывы и рейтинги товаров
- ✅ Администраторская панель Django
- ✅ REST API (DRF + Swagger)
- ✅ Тёмная/светлая тема
- ✅ Полностью адаптивный дизайн

## Развёртывание

### Локальное развёртывание

1. Клонируйте репозиторий
2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Примените миграции:
```bash
python manage.py migrate
```

5. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

6. Запустите сервер разработки:
```bash
python manage.py runserver
```

Сайт доступен по адресу: http://127.0.0.1:8000

### Production развёртывание

Смотрите [DEPLOYMENT.md](DEPLOYMENT.md) для подробных инструкций по развёртыванию на реальном сервере.

## Структура проекта

```
project-zt/
├── shops/               # Основные настройки Django
├── store/              # Основное приложение
│   ├── models.py       # Модели БД
│   ├── views.py        # Представления
│   ├── urls.py         # URL маршруты
│   └── templates/      # HTML шаблоны
├── media/              # Загруженные файлы (товары, аватары)
├── static/             # Статические файлы (CSS, JS, images)
├── manage.py           # Управление Django
└── db.sqlite3          # База данных (SQLite)
```

## API Документация

REST API доступен по адресу: `/api/v1/`

Swagger документация: `/api/docs/`

## Администраторская панель

Доступна по адресу: `/admin/`

Используйте учётные данные суперпользователя для входа.

## Технологии

- **Backend:** Django 6.0, Python 3.13
- **API:** Django Rest Framework, drf-yasg
- **Database:** SQLite (разработка), PostgreSQL (production)
- **Frontend:** HTML5, CSS3, JavaScript
- **Deployment:** Gunicorn, Nginx, Systemd

## Лицензия

MIT

## Автор

StoreHub - Лучший онлайн магазин
