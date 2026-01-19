from django.contrib import admin
from .models import Category, Product
from .models import Cart, CartItem
from .models import Order, OrderItem
from .models import Favorite, Review, Reservation


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug']
    list_editable = ['name']
    list_display_links = ['id']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'name_ru', 'name_kg', 'price', 'stock']
    list_editable = ['name', 'name_ru', 'price', 'stock']
    list_display_links = ['id']
    fieldsets = (
        (None, {'fields': ('category', 'name', 'name_ru', 'name_kg', 'name_en', 'slug', 'image', 'price', 'stock', 'is_published')}),
        ('Описание', {'fields': ('description', 'description_ru', 'description_kg', 'description_en')}),
    )

    actions = ['autotranslate_selected']

    def autotranslate_selected(self, request, queryset):
        """Admin action: autotranslate selected products using default provider"""
        from django.contrib import messages
        translated = 0
        for p in queryset:
            changed = False
            for lang in ('ru', 'kg', 'en'):
                name_field = f'name_{lang}'
                desc_field = f'description_{lang}'
                cur_name = getattr(p, name_field, None)
                if not cur_name:
                    tr = None
                    try:
                        from store.utils.translate import translate_text
                        tr = translate_text(p.name, target_lang=lang)
                    except Exception:
                        tr = ''
                    if tr:
                        setattr(p, name_field, tr)
                        changed = True
                cur_desc = getattr(p, desc_field, None)
                if not cur_desc:
                    trd = None
                    try:
                        from store.utils.translate import translate_text
                        trd = translate_text(p.description or '', target_lang=lang)
                    except Exception:
                        trd = ''
                    if trd:
                        setattr(p, desc_field, trd)
                        changed = True
            if changed:
                p.save()
                translated += 1
        messages.add_message(request, messages.INFO, f'Автопереведено: {translated} товаров')
    autotranslate_selected.short_description = 'Автоперевести выбранные продукты'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'created_at']
    search_fields = ['session_key', 'user__username']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'quantity', 'price']
    list_filter = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'full_name', 'email']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'name', 'price', 'quantity']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'created_at']
    search_fields = ['user__username', 'product__name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'user', 'rating', 'approved', 'created_at']
    list_filter = ['approved', 'rating']
    search_fields = ['product__name', 'user__username', 'text']


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'user', 'reserved_from', 'reserved_to', 'status']
    list_filter = ['status']