import stripe
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Order, OrderItem, Product
import json

stripe.api_key = settings.STRIPE_SECRET_KEY


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_intent(request):
    """
    Создать платежный намерение для Stripe
    """
    try:
        data = request.data
        order_id = data.get('order_id')
        
        order = Order.objects.get(id=order_id, user=request.user)
        
        intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount * 100),  # Сумма в центах
            currency='kgs',
            metadata={'order_id': order_id, 'user_id': request.user.id}
        )
        
        return Response({
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id
        })
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_payment(request):
    """
    Подтвердить платеж и обновить статус заказа
    """
    try:
        data = request.data
        payment_intent_id = data.get('payment_intent_id')
        
        # Получить PaymentIntent от Stripe
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status == 'succeeded':
            order_id = intent.metadata.get('order_id')
            order = Order.objects.get(id=order_id)
            order.status = 'paid'
            order.save()
            
            return Response({
                'success': True,
                'message': 'Payment successful',
                'order_id': order_id
            })
        else:
            return Response({
                'success': False,
                'message': f'Payment failed: {intent.status}'
            }, status=400)
            
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def seller_earnings(request):
    """
    Получить доход продавца
    """
    user = request.user
    seller_orders = OrderItem.objects.filter(
        order__status='paid',
        order__items__product__owner=user
    ).distinct()
    
    total_earned = sum([item.subtotal() for item in seller_orders])
    commission = (total_earned * settings.SELLER_COMMISSION_PERCENTAGE) / 100
    net_earnings = total_earned - commission
    
    return Response({
        'gross_earnings': total_earned,
        'commission': commission,
        'net_earnings': net_earnings,
        'orders_count': seller_orders.count()
    })
