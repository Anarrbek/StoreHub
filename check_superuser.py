import os
import django
from django.conf import settings

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shops.settings')
django.setup()

from django.contrib.auth.models import User

# Проверка супер пользователей
superusers = User.objects.filter(is_superuser=True)
if superusers.exists():
    for user in superusers:
        print(f"Супер пользователь: {user.username}, email: {user.email}")
else:
    print("Супер пользователи не найдены.")