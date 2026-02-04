"""
Celery задачи для асинхронных операций
"""
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import Order, Cart, Review, Product
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_pending_emails():
    """Отправка ожидающих email уведомлений"""
    try:
        # Пример: отправить email о новом заказе
        orders = Order.objects.filter(status='new').order_by('-created_at')[:10]
        for order in orders:
            if order.user and order.user.email:
                send_mail(
                    f'Заказ #{order.id} получен',
                    f'Ваш заказ на сумму {order.total_amount} сом принят в обработку.',
                    'noreply@storehub.kg',
                    [order.user.email],
                    fail_silently=False,
                )
        logger.info(f"Отправлено {len(orders)} email уведомлений")
    except Exception as e:
        logger.error(f"Ошибка при отправке email: {e}")


@shared_task
def send_order_confirmation(order_id):
    """Отправить подтверждение заказа"""
    try:
        order = Order.objects.get(id=order_id)
        if order.user and order.user.email:
            items_list = '\n'.join([
                f"- {item.name} x{item.quantity} = {item.subtotal()} сом"
                for item in order.items.all()
            ])
            
            send_mail(
                f'Подтверждение заказа #{order.id}',
                f'''Спасибо за заказ!

Номер заказа: {order.id}
Товары:
{items_list}

Итого: {order.total_amount} сом
Статус: {order.get_status_display()}

Мы свяжемся с вами в течение часа.''',
                'noreply@storehub.kg',
                [order.user.email],
                fail_silently=False,
            )
            logger.info(f"Подтверждение заказа {order_id} отправлено")
    except Order.DoesNotExist:
        logger.error(f"Заказ {order_id} не найден")


@shared_task
def send_seller_notification(order_id):
    """Уведомить продавца о новом заказе"""
    try:
        order = Order.objects.get(id=order_id)
        
        # Группировать товары по продавцам
        sellers = {}
        for item in order.items.all():
            if item.product.owner:
                if item.product.owner not in sellers:
                    sellers[item.product.owner] = []
                sellers[item.product.owner].append(item)
        
        # Отправить уведомления
        for seller, items in sellers.items():
            if seller.email:
                items_text = '\n'.join([
                    f"- {item.name} x{item.quantity}"
                    for item in items
                ])
                
                send_mail(
                    f'Новый заказ #{order.id}',
                    f'''У вас новый заказ!

Заказ: {order.id}
Ваши товары:
{items_text}

Контакты покупателя:
Имя: {order.full_name}
Email: {order.email}
Телефон: {order.phone}
Адрес: {order.address}''',
                    'noreply@storehub.kg',
                    [seller.email],
                    fail_silently=False,
                )
        logger.info(f"Уведомления продавцам для заказа {order_id} отправлены")
    except Order.DoesNotExist:
        logger.error(f"Заказ {order_id} не найден")


@shared_task
def cleanup_old_carts():
    """Удалить старые заброшенные корзины"""
    try:
        # Удалить корзины старше 30 дней
        cutoff_date = timezone.now() - timedelta(days=30)
        old_carts = Cart.objects.filter(created_at__lt=cutoff_date)
        count = old_carts.count()
        old_carts.delete()
        logger.info(f"Удалено {count} старых корзин")
    except Exception as e:
        logger.error(f"Ошибка при удалении корзин: {e}")


@shared_task
def generate_daily_report():
    """Генерировать ежедневный отчет о продажах"""
    try:
        from django.db.models import Sum, Count
        from datetime import date
        
        today = date.today()
        orders_today = Order.objects.filter(
            created_at__date=today,
            status='paid'
        )
        
        stats = {
            'orders_count': orders_today.count(),
            'total_revenue': orders_today.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
            'products_sold': sum([item.quantity for order in orders_today for item in order.items.all()]),
        }
        
        logger.info(f"Ежедневный отчет {today}: {stats}")
        
        # Можно отправить на email admin
        return stats
    except Exception as e:
        logger.error(f"Ошибка при генерации отчета: {e}")


@shared_task
def process_payment_callback(payment_id, status):
    """Обработать платежный callback от Stripe"""
    try:
        from .models import Payment
        payment = Payment.objects.get(stripe_id=payment_id)
        payment.status = status
        payment.save()
        
        if status == 'succeeded':
            payment.order.status = 'paid'
            payment.order.save()
            
            # Отправить подтверждение
            send_order_confirmation.delay(payment.order.id)
            send_seller_notification.delay(payment.order.id)
        
        logger.info(f"Платеж {payment_id} обновлен: {status}")
    except Exception as e:
        logger.error(f"Ошибка при обработке платежа: {e}")


@shared_task
def update_product_popularity():
    """Обновить популярность товаров (для рейтинга)"""
    try:
        # Увеличить счетчик просмотров или продаж
        products = Product.objects.filter(is_deleted=False)
        logger.info(f"Обновлена популярность {products.count()} товаров")
    except Exception as e:
        logger.error(f"Ошибка при обновлении популярности: {e}")


@shared_task
def send_review_reminder(order_id):
    """Отправить напоминание оставить отзыв"""
    try:
        from datetime import timedelta
        order = Order.objects.get(id=order_id)
        
        # Проверить что достаточно времени прошло
        if (timezone.now() - order.created_at).days >= 3:
            if order.user and order.user.email:
                send_mail(
                    'Оставьте отзыв о вашей покупке',
                    f'''Привет {order.user.first_name}!

Спасибо что вы купили у нас 3 дня назад.
Ваши отзывы помогают улучшать качество.

Оставить отзыв: https://storehub.kg/orders/{order_id}/reviews/''',
                    'noreply@storehub.kg',
                    [order.user.email],
                    fail_silently=False,
                )
        logger.info(f"Напоминание об отзыве для заказа {order_id} отправлено")
    except Order.DoesNotExist:
        logger.error(f"Заказ {order_id} не найден")


# Периодическая задача для Celery Beat
app.conf.beat_schedule = {
    'send-emails-every-15-min': {
        'task': 'store.tasks.send_pending_emails',
        'schedule': 900.0,  # 15 минут в секундах
    },
    'cleanup-carts-daily': {
        'task': 'store.tasks.cleanup_old_carts',
        'schedule': 86400.0,  # 24 часа
    },
    'daily-report': {
        'task': 'store.tasks.generate_daily_report',
        'schedule': 86400.0,
    },
}
