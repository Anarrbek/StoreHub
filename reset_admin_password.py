import os
import django
from django.conf import settings

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shops.settings')
django.setup()

from django.contrib.auth.models import User

# Изменение пароля для admin
username = 'admin'
new_password = 'admin123'

user = User.objects.filter(username=username).first()
if user:
    user.set_password(new_password)
    user.save()
    print(f"Пароль для '{username}' сброшен на '{new_password}'")
else:
    print(f"Пользователь '{username}' не найден.")