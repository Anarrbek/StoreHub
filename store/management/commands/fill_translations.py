from django.core.management.base import BaseCommand
from store.models import Product

class Command(BaseCommand):
    help = 'Fill empty translation fields for products using original text (name, description)'

    def handle(self, *args, **options):
        products = Product.objects.all()
        updated = 0
        for p in products:
            changed = False
            if not p.name_ru:
                p.name_ru = p.name
                changed = True
            if not p.name_kg:
                p.name_kg = p.name
                changed = True
            if not getattr(p, 'name_en', None):
                p.name_en = p.name
                changed = True
            if not getattr(p, 'description_ru', None):
                p.description_ru = p.description
                changed = True
            if not getattr(p, 'description_kg', None):
                p.description_kg = p.description
                changed = True
            if not getattr(p, 'description_en', None):
                p.description_en = p.description
                changed = True
            if changed:
                p.save()
                updated += 1
        self.stdout.write(self.style.SUCCESS(f'Updated translations for {updated} products'))