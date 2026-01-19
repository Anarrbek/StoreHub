from django.core.management.base import BaseCommand
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Seed default categories for the store'

    def handle(self, *args, **options):
        from store.models import Category

        names = [
            'Одежда',
            'Электро техника',
            'Смартфоны',
            'Авто',
            'Бытовая техника',
        ]

        for name in names:
            slug = slugify(name, allow_unicode=True)
            obj, created = Category.objects.get_or_create(slug=slug, defaults={'name': name})
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {name} ({slug})'))
            else:
                self.stdout.write(self.style.NOTICE(f'Already exists: {name} ({slug})'))

        self.stdout.write(self.style.SUCCESS('Seeding complete.'))
