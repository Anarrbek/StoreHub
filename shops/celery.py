"""
Celery конфигурация для фоновых задач
"""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shops.settings')

app = Celery('shops')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Периодические задачи
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

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
