import os
import django
from django.conf import settings

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shops.settings')
django.setup()

from django.contrib.auth.models import User

# Создание супер пользователя, если не существует
username = 'admin'
email = 'admin@example.com'
password = 'admin123'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Супер пользователь '{username}' создан. Пароль: {password}")
else:
    print(f"Супер пользователь '{username}' уже существует.")