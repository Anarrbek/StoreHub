import os
import django
from django.conf import settings

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shops.settings')
django.setup()

from django.contrib.auth.models import User

# Проверка пользователя
username = 'Anarbek_009'
user = User.objects.filter(username=username).first()
if user:
    print(f"Пользователь {username} существует.")
    print(f"Email: {user.email}")
    print(f"Активен: {user.is_active}")
    print(f"Суперпользователь: {user.is_superuser}")
else:
    print(f"Пользователь {username} не найден.")