# Email система уведомлений

## Конфигурация

Всё уже настроено в `shops/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'noreply@storehub.kg'
```

## Провайдеры Email

### 1. Gmail (бесплатно, для разработки)

```bash
# Включить 2-factor auth на Gmail
# Создать App Password: https://myaccount.google.com/apppasswords

# .env:
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
```

### 2. SendGrid (профессионально, 100 писем/день бесплатно)

```bash
# Зарегистрироваться на https://sendgrid.com/
# Скопировать API Key

# .env:
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
SENDGRID_API_KEY=SG.xxxxxx...

# pip install sendgrid-django
```

### 3. Mailgun (100 писем/месяц бесплатно)

```bash
# Зарегистрироваться на https://www.mailgun.com/
# Получить domain и API key

# .env:
EMAIL_BACKEND=anymail.backends.mailgun.EmailBackend
ANYMAIL={
    "MAILGUN_API_KEY": "key-xxxxx",
    "MAILGUN_SENDER_DOMAIN": "mg.yourdomain.com",
}

# pip install django-anymail[mailgun]
```

### 4. Яндекс.Облако (для .kg домена)

```bash
# Зарегистрироваться на https://cloud.yandex.kg/

# .env:
EMAIL_HOST=smtp.yandex.kg
EMAIL_PORT=587
EMAIL_HOST_USER=support@storehub.kg
EMAIL_HOST_PASSWORD=app-password
```

## Использование в коде

### Отправить простой email

```python
from django.core.mail import send_mail

send_mail(
    subject='Новый заказ',
    message='Ваш заказ принят',
    from_email='noreply@storehub.kg',
    recipient_list=['customer@example.com'],
    fail_silently=False,
)
```

### Отправить HTML email

```python
from django.core.mail import EmailMultiAlternatives

msg = EmailMultiAlternatives(
    subject='Новый заказ #123',
    body='Ваш заказ принят',
    from_email='noreply@storehub.kg',
    to=['customer@example.com']
)

html_content = """
<h2>Спасибо за заказ!</h2>
<p>Номер заказа: <b>#123</b></p>
<a href="https://storehub.kg/orders/123/">Просмотреть заказ</a>
"""

msg.attach_alternative(html_content, "text/html")
msg.send()
```

### С attachments (файлы)

```python
from django.core.mail import EmailMessage

msg = EmailMessage(
    subject='Invoice',
    body='See attached invoice',
    from_email='noreply@storehub.kg',
    to=['customer@example.com']
)

with open('invoice.pdf', 'rb') as attachment:
    msg.attach(
        'invoice.pdf',
        attachment.read(),
        'application/pdf'
    )

msg.send()
```

## Асинхронная отправка (Celery)

**Рекомендуется для production!**

```python
# store/tasks.py уже содержит:

@shared_task
def send_order_confirmation(order_id):
    order = Order.objects.get(id=order_id)
    send_mail(
        subject=f'Заказ #{order.id}',
        message=f'Сумма: {order.total_amount} сом',
        from_email='noreply@storehub.kg',
        recipient_list=[order.user.email],
    )

# В view:
def create_order(request):
    order = Order.objects.create(...)
    send_order_confirmation.delay(order.id)  # Отправится в фоне!
    return redirect('order_confirm', order_id=order.id)
```

## Шаблоны (Template-based)

### Создать шаблон

Создать `store/templates/emails/order_confirmation.html`:

```html
<h1>Спасибо за заказ!</h1>
<p>Номер заказа: <b>#{{ order.id }}</b></p>

<h2>Товары:</h2>
<ul>
  {% for item in order.items.all %}
    <li>{{ item.name }} x{{ item.quantity }} = {{ item.subtotal }} сом</li>
  {% endfor %}
</ul>

<p><b>Итого: {{ order.total_amount }} сом</b></p>
<a href="https://storehub.kg/orders/{{ order.id }}/">Отследить заказ</a>
```

### Отправить через шаблон

```python
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

def send_order_email(order):
    context = {'order': order}
    html_content = render_to_string('emails/order_confirmation.html', context)
    
    msg = EmailMultiAlternatives(
        subject=f'Заказ #{order.id}',
        body='Смотрите в HTML-версии',
        from_email='noreply@storehub.kg',
        to=[order.user.email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
```

## .env переменные

```bash
# SMTP для Gmail
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx

# Или для Яндекса
EMAIL_HOST=smtp.yandex.kg
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=support@storehub.kg
EMAIL_HOST_PASSWORD=your-app-password

# От кого отправляется письмо
DEFAULT_FROM_EMAIL=noreply@storehub.kg

# На почту админа (для error emails)
ADMIN_EMAIL=admin@storehub.kg
```

## Тестирование

### Локальное тестирование (безопасно)

Добавить в settings.py:

```python
# Вывести письма в консоль вместо отправки
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Или в .env:
```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Тестирование с файлом

```python
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'sent_emails')
```

Письма сохранятся в `sent_emails/` директорию.

### В shell

```bash
python manage.py shell

from django.core.mail import send_mail

send_mail(
    'Test',
    'Hello World',
    'noreply@storehub.kg',
    ['test@example.com'],
    fail_silently=False,
)
```

## Production Checklist

- [ ] Выбран провайдер (SendGrid, Mailgun, Яндекс)
- [ ] Получен API Key или пароль
- [ ] .env переменные установлены
- [ ] Протестировано отправка письма
- [ ] Включен HTTPS (обязательно для важных email)
- [ ] Настроено резервное отправление (retry)
- [ ] Настроены HTML шаблоны
- [ ] Добавлены unsubscribe ссылки (GDPR)
- [ ] Настроено логирование ошибок при отправке
- [ ] Celery worker запущен для async отправки

## Автоматические уведомления (уже реализованы)

### Новый заказ
- Отправляется покупателю (подтверждение)
- Отправляется продавцу (новый заказ)

### Контакт с продавцом
- Отправляется продавцу (новое сообщение)

### Платеж
- Отправляется после успешного платежа
- Отправляется если платеж не прошел

### Напоминание об отзыве
- Отправляется через 3 дня после заказа

## Дальнейшее развитие

- [ ] SMS уведомления (Twilio)
- [ ] Push-уведомления (Firebase)
- [ ] Notifiactions в приложении (WebSocket)
- [ ] Email campaigns (Mailchimp)
- [ ] Newsletter (Django-newsletter)
- [ ] Unsubscribe management (GDPR)

## Troubleshooting

### "Connection refused" при отправке
- Проверить EMAIL_HOST и EMAIL_PORT
- Проверить firewall
- Для Gmail - требует App Password, не обычный пароль

### "Authentication failed"
- Проверить EMAIL_HOST_USER и EMAIL_HOST_PASSWORD
- Для Gmail - включить 2FA и создать App Password
- Для Яндекса - использовать пароль от приложения

### Письма идут в спам
- Добавить SPF запись DNS
- Добавить DKIM подпись
- Добавить DMARC политику
- Использовать настоящий домен, не @gmail.com

```bash
# SPF запись в DNS:
v=spf1 include:sendgrid.net ~all

# DKIM добавить через SendGrid/Mailgun консоль
```

## Стоимость

| Провайдер | Цена | Лимит | Плюсы |
|-----------|------|-------|-------|
| Gmail | 0 | 500/день | Просто, бесплатно |
| SendGrid | 0-80$/мес | 100 писем/день (free) | Надежный, тех. поддержка |
| Mailgun | 0-35$/мес | 100 писем/месяц (free) | API, cheap |
| Яндекс.Облако | 0 | Не ограничено | Для .kg домена |

**Рекомендация**: SendGrid для стартапа, Яндекс.Облако для локального рынка.
