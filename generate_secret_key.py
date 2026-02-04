#!/usr/bin/env python
"""
Генератор SECRET_KEY для Django production

Использование:
    python generate_secret_key.py
"""

from django.core.management.utils import get_random_secret_key

if __name__ == '__main__':
    print("=" * 50)
    print("Django SECRET_KEY Generator")
    print("=" * 50)
    print()
    
    key = get_random_secret_key()
    
    print("Новый SECRET_KEY для .env файла:")
    print()
    print(f"SECRET_KEY={key}")
    print()
    print("Скопируйте эту строку в ваш .env файл")
    print("=" * 50)
