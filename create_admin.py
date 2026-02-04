#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shops.settings')
django.setup()

from django.contrib.auth.models import User

# Удалим старого admin если существует
User.objects.filter(username='admin').delete()

# Создадим нового
user = User.objects.create_superuser('admin', 'admin@example.com', 'Admin123456')
print(f"Суперпользователь создан: {user.username}")
print(f"Email: {user.email}")
print(f"Пароль: Admin123456")
