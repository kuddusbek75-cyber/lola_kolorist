"""Отправка заявок в Telegram-бот (CRM). Получают только админы, прошедшие пароль."""
import logging
import threading
from html import escape

import requests
from django.conf import settings

from .models import TelegramAdmin

logger = logging.getLogger(__name__)
API_URL = 'https://api.telegram.org/bot{token}/{method}'


def call_api(method, payload=None, timeout=(3, 10)):
    """Вызов Bot API. Возвращает dict или None. Токен в логи не попадает."""
    token = getattr(settings, 'BOT_TOKEN', '')
    if not token:
        logger.warning('BOT_TOKEN не задан в .env')
        return None
    try:
        response = requests.post(API_URL.format(token=token, method=method),
                                 data=payload or {}, timeout=timeout)
        data = response.json()
        if not data.get('ok'):
            logger.error('Telegram %s: %s %s', method, response.status_code, data.get('description'))
            return None
        return data
    except (requests.RequestException, ValueError) as exc:
        logger.error('Telegram %s failed: %s', method, type(exc).__name__)
        return None


def send_telegram_message(text, chat_id):
    return call_api('sendMessage', {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}) is not None


def build_new_booking_message(b):
    return (
        '<b>🆕 Новая запись</b>\n\n'
        f'<b>Имя:</b> {escape(b.first_name)}\n'
        f'<b>Фамилия:</b> {escape(b.last_name)}\n'
        f'<b>Телефон:</b> {escape(b.phone)}\n'
        f'<b>Что нужно сделать:</b> {escape(b.wish)}\n'
        f'<b>Дата:</b> {b.date:%d.%m.%Y}\n'
        f'<b>Время:</b> {b.time:%H:%M}'
    )


def notify_new_booking(booking):
    """Рассылает заявку всем авторизованным админам."""
    chats = list(TelegramAdmin.objects.values_list('chat_id', flat=True))
    if not chats:
        logger.warning('Нет авторизованных админов: отправьте /start боту.')
        return False
    text = build_new_booking_message(booking)
    sent = any([send_telegram_message(text, c) for c in chats])
    if sent:
        booking.telegram_sent = True
        booking.save(update_fields=['telegram_sent'])
    return sent


def notify_in_background(booking_id):
    """Не заставляем клиента ждать Telegram."""
    def run():
        from .models import Booking
        booking = Booking.objects.filter(pk=booking_id).first()
        if booking:
            notify_new_booking(booking)
    threading.Thread(target=run, daemon=True).start()
