"""
Stripe интеграция для платежей
"""
import stripe
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Payment, Order
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(request, order_id):
    """Создаёт Stripe checkout session для оплаты заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'kgs',
                    'product_data': {
                        'name': f'Order #{order.id}',
                        'description': f'{order.items.count()} items',
                    },
                    'unit_amount': int(order.total_amount * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(f'/order/confirm/{order.id}/'),
            cancel_url=request.build_absolute_uri('/cart/'),
        )
        
        # Создаём запись о платеже
        Payment.objects.create(
            order=order,
            stripe_id=session.id,
            amount=order.total_amount,
            status='pending',
        )
        
        return redirect(session.url)
    except Exception as e:
        messages.error(request, f'Ошибка при создании платежа: {str(e)}')
        return redirect('checkout')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Вебхук от Stripe для обновления статуса платежей"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        try:
            payment = Payment.objects.get(stripe_id=session.id)
            payment.status = 'succeeded'
            payment.save()
            
            order = payment.order
            order.status = 'paid'
            order.save()
        except Payment.DoesNotExist:
            pass
    
    elif event['type'] == 'charge.failed':
        charge = event['data']['object']
        try:
            payment = Payment.objects.get(stripe_id=charge.payment_intent)
            payment.status = 'failed'
            payment.save()
        except Payment.DoesNotExist:
            pass
    
    return JsonResponse({'status': 'success'})


def payment_status(request, order_id):
    """Проверка статуса платежа"""
    order = get_object_or_404(Order, id=order_id)
    
    if hasattr(order, 'payment'):
        return JsonResponse({
            'status': order.payment.status,
            'amount': str(order.payment.amount),
        })
    
    return JsonResponse({'status': 'no_payment'})
