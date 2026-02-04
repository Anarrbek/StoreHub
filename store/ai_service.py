from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def ai_chat_answer(user_message, products_context):
    prompt = f"""
Ты помощник сайта.
Отвечай ТОЛЬКО по информации ниже.
Если информации нет - скажи, что товара нет.

Товары:
{products_context}

Вопрос пользователя:
{user_message}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "context": "Ты помощник интернет-магазина."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=300,
    )

    return response.choices[0].message.content