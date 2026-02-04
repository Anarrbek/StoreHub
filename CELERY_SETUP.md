# Celery для фоновых задач

## Что это такое?

Celery - это распределённая система обработки задач для Django. Позволяет:
- Отправлять email в фоне
- Генерировать отчеты ночью
- Обрабатывать файлы без блокировки
- Выполнять периодические задачи (cron)

## Установка

Уже в requirements.txt:
```
celery==5.3.1
redis==5.0.1
```

Установить:
```bash
pip install -r requirements.txt
```

## Конфигурация

### 1. shops/settings.py (уже настроено)

```python
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 минут
```

### 2. shops/celery.py (уже создан)

Конфиг Celery приложения и периодических задач.

### 3. store/tasks.py (уже создан)

Определены все фоновые задачи:
- `send_pending_emails()` - отправка email уведомлений
- `send_order_confirmation()` - подтверждение заказа
- `send_seller_notification()` - уведомление продавца
- `cleanup_old_carts()` - удаление старых корзин
- `generate_daily_report()` - ежедневный отчет
- `process_payment_callback()` - обработка платежей
- `send_review_reminder()` - напоминание об отзыве

## Запуск локально

### 1. Запустить Redis

```bash
# Windows (если установлен)
redis-server

# Linux
redis-server

# Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### 2. Запустить Celery worker

```bash
celery -A shops worker -l info
```

### 3. Запустить Celery Beat (для периодических задач)

```bash
celery -A shops beat -l info
```

### 4. Запустить Django

```bash
python manage.py runserver
```

## Использование в коде

### Отправить задачу в очередь

```python
from store.tasks import send_order_confirmation

# Асинхронно (отправится в фоне)
send_order_confirmation.delay(order_id)

# С задержкой (через 1 час)
send_order_confirmation.apply_async(
    args=[order_id],
    countdown=3600
)
```

### В view:

```python
from store.tasks import send_order_confirmation

def create_order(request):
    # ... создание заказа ...
    
    # Отправить письмо асинхронно
    send_order_confirmation.delay(order.id)
    
    return redirect('order_confirm', order_id=order.id)
```

## Периодические задачи (Celery Beat)

В `shops/celery.py` определены:

```python
app.conf.beat_schedule = {
    'send-pending-emails': {
        'task': 'store.tasks.send_pending_emails',
        'schedule': crontab(minute='*/15'),  # Каждые 15 минут
    },
    'cleanup-old-carts': {
        'task': 'store.tasks.cleanup_old_carts',
        'schedule': crontab(hour=3, minute=0),  # 3:00 AM
    },
    'generate-daily-report': {
        'task': 'store.tasks.generate_daily_report',
        'schedule': crontab(hour=0, minute=0),  # Полночь
    },
}
```

## С Docker

```bash
# В docker-compose.yml уже определен celery сервис
docker-compose up -d

# Celery worker автоматически запустится
docker-compose logs -f celery

# Celery Beat запустится отдельно
docker-compose run celery celery -A shops beat -l info
```

## Мониторинг

### Flower (веб-интерфейс для Celery)

```bash
pip install flower

# Запустить
celery -A shops events

# В другом терминале
flower -A shops --port=5555
```

Доступен на http://localhost:5555

## Production

### Supervisor (Linux)

Создать `/etc/supervisor/conf.d/celery.conf`:

```ini
[program:celery]
process_name=%(program_name)s
command=celery -A shops worker -l info --concurrency=4
directory=/path/to/project
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery.log

[program:celery-beat]
process_name=%(program_name)s_beat
command=celery -A shops beat -l info
directory=/path/to/project
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery-beat.log
```

Запустить:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start celery celery-beat
```

### Systemd (альтернатива)

Создать `/etc/systemd/system/celery.service`:

```ini
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/project
ExecStart=/path/to/venv/bin/celery -A shops worker -l info
Restart=always

[Install]
WantedBy=multi-user.target
```

## Решение проблем

### "No module named 'store.tasks'"
- Убедиться что `store/tasks.py` существует
- Перезагрузить Celery worker

### "Connection refused" (Redis)
- Убедиться что Redis запущен
- Проверить `CELERY_BROKER_URL` в settings.py

### Задача не выполняется
- Проверить логи worker'а
- Убедиться что @shared_task декоратор использован

### Высокая нагрузка
- Увеличить количество workers
- Увеличить concurrency: `celery -A shops worker -l info --concurrency=8`
- Использовать Celery pools (prefork, solo, threads, eventlet)

## Performance Tips

1. **Сериализация**: Используется JSON (медленнее, но безопаснее)
2. **Timeout**: Установлен 30 минут - увеличить для долгих задач
3. **Retry**: Настроить retry логику для важных задач
4. **Monitoring**: Использовать Flower для контроля

```python
# Пример с retry
@shared_task(bind=True, max_retries=3)
def my_task(self):
    try:
        # ... код ...
    except Exception as exc:
        self.retry(exc=exc, countdown=60)  # Повтор через 60 сек
```

## Дальнейшее развитие

- [ ] Настроить автоматический retry при ошибках
- [ ] Добавить Flower для мониторинга
- [ ] Создать dashboard для истории задач
- [ ] Настроить уведомления при критических ошибках
- [ ] Добавить rate limiting для задач
