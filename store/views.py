from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .forms import ProductForm, RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Category, Product, Cart, CartItem
from .models import Order, OrderItem
from .models import Favorite, Review, Reservation
from .forms import CategoryForm
from django.utils.text import slugify
from django.core.paginator import Paginator

def _unique_slug_for_model(model, base_slug):
    """Return a unique slug for given model by appending -1, -2... if needed."""
    slug = base_slug
    counter = 1
    while model.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug
from rest_framework import viewsets
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


def home(request):
    # Главная страница маркетплейса с товарами и баннерами
    products = Product.objects.filter(is_deleted=False, is_published=True).order_by('-created_at')[:10]
    language = request.session.get('lang', 'ru')
    favorites_set = set()
    if request.user.is_authenticated:
        favorites_set = set(Favorite.objects.filter(user=request.user).values_list('product_id', flat=True))
    return render(request, 'store/index_marketplace.html', {
        'products': products,
        'language': language,
        'favorites_set': favorites_set
    })


def theme_main(request):
    # reuse the same simple page for theme demo
    return render(request, 'store/simple_page.html', {'title':'Тема', 'content':'Здесь можно переключать светлую/тёмную тему через кнопку.'})


def product_list(request):
    products = Product.objects.filter(is_deleted=False, is_published=True).order_by('-created_at')
    
    # Пагинация: 15 товаров на странице
    paginator = Paginator(products, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    language = request.session.get('lang', 'ru')
    favorites_set = set()
    if request.user.is_authenticated:
        favorites_set = set(Favorite.objects.filter(user=request.user).values_list('product_id', flat=True))
    return render(request, 'store/product_list.html', {
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'language': language,
        'favorites_set': favorites_set
    })


def set_language(request):
    lang = request.GET.get('lang')
    if lang in ('ru', 'kg', 'en'):
        request.session['lang'] = lang
    next_url = request.META.get('HTTP_REFERER') or '/'
    return redirect(next_url)


def add_product(request):
    created = False
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            # если категория не выбрана — используем или создаём 'Uncategorized'
            if not product.category_id:
                cat, _ = Category.objects.get_or_create(name='Uncategorized', slug='uncategorized')
                product.category = cat
            # generate slug from name if empty
            if not getattr(product, 'slug', None):
                base = slugify(product.name, allow_unicode=True)
                product.slug = _unique_slug_for_model(Product, base)
            # пометим как опубликованный по умолчанию, чтобы сразу видеть
            product.is_published = True
            product.save()
            created = True
            return redirect('product_detail', slug=product.slug)
        else:
            # форма невалидна — покажем ошибки
            pass
    else:
        form = ProductForm()
    return render(request, 'store/add_product.html', {'form': form, 'created': created})


def rules(request):
    rules_list = [
        'Не размещать запрещённые товары.',
        'Указывайте правдивое описание и цену.',
        'Уважайте других пользователей.'
    ]
    return render(request, 'store/simple_page.html', {'title':'Правила сайта', 'items': rules_list})


def faq(request):
    faqs = [
        {'title':'Как добавить товар?', 'text':'Через страницу «Добавить товар» — заполните форму и отправьте.'},
        {'title':'Как оплатить?', 'text':'В этой учебной версии оплата пока не реализована.'}
    ]
    return render(request, 'store/simple_page.html', {'title':'Вопросы и ответы', 'items': faqs})


def add_category(request):
    created = False
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            # generate slug from name
            base = slugify(cat.name, allow_unicode=True)
            cat.slug = _unique_slug_for_model(Category, base)
            cat.save()
            created = True
        else:
            pass
    else:
        form = CategoryForm()
    return render(request, 'store/add_category.html', {'form': form, 'created': created})


def product_detail(request, slug):
    product = Product.objects.filter(slug=slug, is_deleted=False).first()
    if not product:
        return HttpResponse('Товар не найден', status=404)
    # include reviews and favorite state
    reviews = product.reviews.filter(approved=True).order_by('-created_at')
    is_fav = False
    favorites_set = set()
    if request.user.is_authenticated:
        is_fav = Favorite.objects.filter(user=request.user, product=product).exists()
        favorites_set = set(Favorite.objects.filter(user=request.user).values_list('product_id', flat=True))
    language = request.session.get('lang', 'ru')
    return render(request, 'store/product_detail.html', {'product': product, 'reviews': reviews, 'is_fav': is_fav, 'language': language, 'favorites_set': favorites_set})


def cart_update_quantity(request, item_id):
    cart = _get_cart(request)
    item = CartItem.objects.filter(pk=item_id, cart=cart).first()
    if not item:
        return redirect('cart_view')
    try:
        qty = int(request.POST.get('quantity', item.quantity))
        if qty < 1:
            prod = item.product
            item.delete()
            try:
                if prod and not CartItem.objects.filter(product=prod).exists():
                    prod.is_published = True
                    prod.save()
                    messages.success(request, 'Товар восстановлён в каталоге')
            except Exception:
                pass
        else:
            item.quantity = qty
            item.save()
    except Exception:
        pass
    return redirect('cart_view')


def product_delete(request, pk):
    product = Product.objects.filter(pk=pk).first()
    if not product:
        return HttpResponse('Товар не найден', status=404)
    if request.method == 'POST':
        # soft-delete: mark product deleted and add a recovery item to the user's cart
        product.is_deleted = True
        product.save()
        cart = _get_cart(request)
        # add to cart as a deleted-backup item (quantity 1)
        item_qs = CartItem.objects.filter(cart=cart, product=product)
        if item_qs.exists():
            item = item_qs.first()
            item.is_deleted_backup = True
            item.quantity = max(1, item.quantity)
            item.price = product.price
            item.save()
        else:
            CartItem.objects.create(cart=cart, product=product, quantity=1, price=product.price, is_deleted_backup=True)
        return redirect('product_list')
    return render(request, 'store/product_confirm_delete.html', {'product': product})


def favorites_list(request):
    if not request.user.is_authenticated:
        return redirect('login')
    favs = Favorite.objects.filter(user=request.user).select_related('product')
    # pass list of product objects to the favorites_list template
    products = [f.product for f in favs]
    language = request.COOKIES.get('language', 'ru')
    return render(request, 'store/favorites_list.html', {'products': products, 'language': language})


def fav_add(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')
    product = get_object_or_404(Product, pk=product_id)
    Favorite.objects.get_or_create(user=request.user, product=product)
    messages.success(request, 'Товар добавлен в избранное')
    # redirect back to product page if there is a referrer, otherwise to favorites
    next_url = request.META.get('HTTP_REFERER') or '/'
    return redirect(next_url)


def fav_remove(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')
    Favorite.objects.filter(user=request.user, product_id=product_id).delete()
    messages.success(request, 'Товар удалён из избранного')
    next_url = request.META.get('HTTP_REFERER') or '/'
    return redirect(next_url)


def review_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        text = request.POST.get('text', '')
        Review.objects.create(user=request.user if request.user.is_authenticated else None,
                              product=product, rating=rating, text=text, approved=False)
        return redirect('product_detail', slug=product.slug)
    return render(request, 'store/review_add.html', {'product': product})


from django.utils.dateparse import parse_datetime


def reserve_view(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        frm = request.POST.get('from')
        to = request.POST.get('to')
        # try parse ISO datetimes (simple)
        try:
            dfrom = parse_datetime(frm)
            dto = parse_datetime(to)
            Reservation.objects.create(user=request.user if request.user.is_authenticated else None,
                                       product=product, reserved_from=dfrom, reserved_to=dto)
            messages.success(request, 'Бронирование оформлено. Мы свяжемся с вами для подтверждения.')
            return redirect('product_detail', slug=product.slug)
        except Exception:
            messages.error(request, 'Не удалось распознать дату. Используйте формат YYYY-MM-DD HH:MM')
    return render(request, 'store/reserve.html', {'product': product})


def reservations_list(request):
    if not request.user.is_authenticated:
        return redirect('login')
    reservations = Reservation.objects.filter(user=request.user).select_related('product').order_by('-created_at')
    # Вычисляем итоговую сумму
    total_price = sum(r.product.price for r in reservations)
    language = request.COOKIES.get('language', 'ru')
    return render(request, 'store/reservations.html', {
        'reservations': reservations,
        'total_price': total_price,
        'language': language
    })


def cancel_reservation(request, res_id):
    res = Reservation.objects.filter(pk=res_id).first()
    if not res:
        messages.error(request, 'Бронь не найдена')
        return redirect('reservations')
    if res.user != request.user:
        messages.error(request, 'Нет доступа')
        return redirect('reservations')
    res.delete()
    messages.success(request, 'Бронь отменена')
    return redirect('reservations')


def search_view(request):
    q = request.GET.get('q', '').strip()
    qs = Product.objects.all()
    if q:
        qs = qs.filter(name__icontains=q)
    language = request.session.get('lang', 'ru')
    return render(request, 'store/search_results.html', {'products': qs, 'query': q, 'language': language})


def _ensure_session(request):
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


def _get_cart(request):
    # Prefer cart for authenticated user, otherwise session-based cart
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart
    session_key = _ensure_session(request)
    cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart


def cart_view(request):
    cart = _get_cart(request)
    items = cart.items.select_related('product').all()
    total = cart.total()
    # Есть ли товары, которые можно оформить (не резервные/удалённые)
    has_purchasable = any(not it.is_deleted_backup for it in items)
    return render(request, 'store/cart.html', {'cart': cart, 'items': items, 'total': total, 'has_purchasable': has_purchasable})


def cart_add(request, product_id):
    product = Product.objects.filter(pk=product_id, is_deleted=False).first()
    if not product:
        return redirect('product_list')
    cart = _get_cart(request)
    qty = 1
    try:
        qty = int(request.POST.get('quantity', 1))
        if qty < 1:
            qty = 1
    except Exception:
        qty = 1
    # either update existing CartItem or create new
    item_qs = CartItem.objects.filter(cart=cart, product=product)
    if item_qs.exists():
        item = item_qs.first()
        item.quantity += qty
        item.save()
    else:
        CartItem.objects.create(cart=cart, product=product, quantity=qty, price=product.price)
    # Hide product from catalog once added to cart (prevent others seeing it)
    try:
        product.is_published = False
        product.save()
        messages.info(request, 'Товар добавлен в корзину и временно скрыт из каталога')
    except Exception:
        pass
    return redirect('cart_view')


def cart_remove(request, item_id):
    cart = _get_cart(request)
    item = CartItem.objects.filter(pk=item_id, cart=cart).first()
    if item:
        prod = item.product
        item.delete()
        # restore product visibility if no other carts contain it
        try:
            if prod and not CartItem.objects.filter(product=prod).exists():
                prod.is_published = True
                prod.save()
                messages.success(request, 'Товар восстановлён в каталоге')
        except Exception:
            pass
    return redirect('cart_view')


def cart_restore(request, item_id):
    # restore a previously deleted product from cart backup
    cart = _get_cart(request)
    item = CartItem.objects.filter(pk=item_id, cart=cart, is_deleted_backup=True).first()
    if not item:
        return redirect('cart_view')
    product = item.product
    product.is_deleted = False
    product.save()
    # remove the backup item from cart
    item.delete()
    return redirect('cart_view')


def _merge_session_cart_to_user(request, user):
    # merge items from a session cart into the user's cart after login
    session_key = request.session.session_key
    if not session_key:
        return
    session_cart = Cart.objects.filter(session_key=session_key).first()
    if not session_cart:
        return
    user_cart, _ = Cart.objects.get_or_create(user=user)
    for item in session_cart.items.all():
        existing = CartItem.objects.filter(cart=user_cart, product=item.product).first()
        if existing:
            existing.quantity += item.quantity
            existing.save()
        else:
            item.cart = user_cart
            item.save()
    # remove the old session cart
    try:
        session_cart.delete()
    except Exception:
        pass


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # auto-login after register
            user = authenticate(username=user.username, password=form.cleaned_data['password'])
            if user:
                login(request, user)
                _merge_session_cart_to_user(request, user)
                return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'store/register.html', {'form': form})


def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            _merge_session_cart_to_user(request, user)
            return redirect('home')
        else:
            error = 'Неверные учётные данные'
    return render(request, 'store/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('home')


def checkout_view(request):
    cart = _get_cart(request)
    items = cart.items.select_related('product').all()
    total = cart.total()
    # simple stubbed checkout page (payment is a placeholder)
    if request.method == 'POST':
        # create Order from cart
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            total_amount=total,
        )
        for it in items:
            OrderItem.objects.create(
                order=order,
                product=it.product,
                name=it.product.name if it.product else it.product_id,
                price=it.price,
                quantity=it.quantity,
            )
            # decrement stock when ordering
            try:
                if it.product and it.product.stock >= it.quantity:
                    it.product.stock = max(0, it.product.stock - it.quantity)
                    # if stock runs out, hide product; otherwise make it visible
                    it.product.is_published = False if it.product.stock == 0 else True
                    it.product.save()
            except Exception:
                pass
        # clear cart
        cart.items.all().delete()
        messages.success(request, 'Заказ оформлен. Спасибо!')
        return redirect('order_confirm', order_id=order.id)
    return render(request, 'store/checkout.html', {'cart': cart, 'items': items, 'total': total})


def order_confirm(request, order_id):
    order = Order.objects.filter(pk=order_id).first()
    if not order:
        return HttpResponse('Заказ не найден', status=404)
    return render(request, 'store/order_confirm.html', {'order': order})


def buy_now(request, product_id):
    product = Product.objects.filter(pk=product_id, is_deleted=False).first()
    if not product:
        messages.error(request, 'Товар не найден')
        return redirect('product_list')
    if request.method == 'POST':
        try:
            qty = int(request.POST.get('quantity', 1))
        except Exception:
            qty = 1
        qty = max(1, qty)
        total = product.price * qty
        order = Order.objects.create(user=request.user if request.user.is_authenticated else None, total_amount=total)
        OrderItem.objects.create(order=order, product=product, name=product.name, price=product.price, quantity=qty)
        # decrement stock
        try:
            if product.stock >= qty:
                product.stock = max(0, product.stock - qty)
                # if stock == 0 hide product
                product.is_published = False if product.stock == 0 else True
                product.save()
        except Exception:
            pass
        messages.success(request, 'Заказ оформлен. Спасибо!')
        return redirect('order_confirm', order_id=order.id)
    return redirect('product_detail', slug=product.slug)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
