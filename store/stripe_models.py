from django.db import models
from django.conf import settings

class Payment(models.Model):
    """Модель платежей для Stripe интеграции"""
    STATUS_CHOICES = (
        ('pending', 'Ожидание'),
        ('succeeded', 'Успешно'),
        ('failed', 'Ошибка'),
        ('refunded', 'Возврат'),
    )
    
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='payment')
    stripe_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    method = models.CharField(max_length=50, default='card')  # card, wallet, etc
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment {self.stripe_id} for Order #{self.order.id}"
