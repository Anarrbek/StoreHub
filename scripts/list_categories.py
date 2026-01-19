from pathlib import Path
import os, sys

# add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shops.settings')
import django
django.setup()

from store.models import Category

cats = Category.objects.all()
if not cats:
    print('No categories found')
else:
    for c in cats:
        print(f'- {c.name} (slug: {c.slug})')
