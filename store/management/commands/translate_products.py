from django.core.management.base import BaseCommand
from store.models import Product
from store.utils.translate import translate_text

class Command(BaseCommand):
    help = 'Autotranslate product names and descriptions using LibreTranslate (fills only empty fields by default)'

    def add_arguments(self, parser):
        parser.add_argument('--provider', default='libre', help='Translation provider (default: libre)')
        parser.add_argument('--langs', default='ru,kg,en', help='Comma-separated target languages: ru,kg,en')
        parser.add_argument('--overwrite', action='store_true', help='Overwrite existing translations')
        parser.add_argument('--limit', type=int, default=0, help='Limit number of products to process (0 = no limit)')

    def handle(self, *args, **options):
        provider = options['provider']
        langs = [l.strip() for l in options['langs'].split(',') if l.strip()]
        overwrite = options['overwrite']
        limit = options['limit']

        qs = Product.objects.all().order_by('id')
        if limit > 0:
            qs = qs[:limit]
        total = 0
        updated = 0
        for p in qs:
            total += 1
            changed = False
            for lang in langs:
                name_field = f'name_{lang}'
                desc_field = f'description_{lang}'
                # name
                cur_name = getattr(p, name_field, None)
                if overwrite or not cur_name:
                    tr = translate_text(p.name, target_lang=lang, provider=provider)
                    if tr:
                        setattr(p, name_field, tr)
                        changed = True
                # description
                cur_desc = getattr(p, desc_field, None)
                if overwrite or not cur_desc:
                    trd = translate_text(p.description or '', target_lang=lang, provider=provider)
                    if trd:
                        setattr(p, desc_field, trd)
                        changed = True
            if changed:
                p.save()
                updated += 1
                self.stdout.write(self.style.SUCCESS(f'Updated product #{p.pk}'))
        self.stdout.write(self.style.SUCCESS(f'Processed {total} products — updated {updated}'))