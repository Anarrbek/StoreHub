import os
import django
from django.conf import settings

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shops.settings')
django.setup()

from django.contrib.auth.models import User

# Изменение пароля для пользователя Anarbek_009
username = 'Anarbek_009'
new_password = 'newpassword123'  # Установите новый пароль

user = User.objects.filter(username=username).first()
if user:
    user.set_password(new_password)
    user.save()
    print(f"Пароль для пользователя {username} изменён на '{new_password}'")
else:
    print(f"Пользователь {username} не найден.")