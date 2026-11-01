"""Обработка сообщений бота. Состояние хранится в базе, подходит для Vercel."""
import hmac
import logging
from datetime import timedelta
from html import escape

from django.conf import settings
from django.utils import timezone

from .models import Booking, BotSession, TelegramAdmin
from .telegram_notify import call_api, send_telegram_message

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 5
BLOCK_MINUTES = 15
MENU = '/bookings - последние заявки\n/logout - выйти'


def reply(chat_id, text):
    send_telegram_message(text, chat_id)


def is_admin(chat_id):
    return TelegramAdmin.objects.filter(chat_id=chat_id).exists()


def handle_start(chat_id):
    if is_admin(chat_id):
        reply(chat_id, '✅ Вы авторизованы.\n\n' + MENU)
        return
    BotSession.objects.update_or_create(chat_id=chat_id, defaults={'awaiting_password': True})
    reply(chat_id, '🔒 Это закрытая CRM-система.\nВведите пароль:')


def handle_password(chat_id, user, message_id, text, session):
    now = timezone.now()
    if session.blocked_until and now < session.blocked_until:
        minutes = int((session.blocked_until - now).total_seconds() // 60) + 1
        reply(chat_id, f'⛔ Слишком много попыток. Повторите через {minutes} мин.')
        return

    call_api('deleteMessage', {'chat_id': chat_id, 'message_id': message_id})

    expected = settings.ADMIN_PASSWORD
    if expected and hmac.compare_digest(text.strip().encode(), expected.encode()):
        TelegramAdmin.objects.update_or_create(chat_id=chat_id, defaults={
            'username': user.get('username', ''),
            'full_name': ' '.join(filter(None, [user.get('first_name'), user.get('last_name')])),
        })
        session.awaiting_password = False
        session.failed_count = 0
        session.blocked_until = None
        session.save()
        reply(chat_id, '✅ Доступ открыт. Новые заявки будут приходить сюда.\n\n' + MENU)
        return

    session.failed_count += 1
    if session.failed_count >= MAX_ATTEMPTS:
        session.failed_count = 0
        session.awaiting_password = False
        session.blocked_until = now + timedelta(minutes=BLOCK_MINUTES)
        session.save()
        reply(chat_id, '⛔ Доступ заблокирован на 15 минут.')
    else:
        session.save()
        reply(chat_id, f'❌ Неверный пароль. Осталось попыток: {MAX_ATTEMPTS - session.failed_count}')


def handle_bookings(chat_id):
    if not is_admin(chat_id):
        reply(chat_id, '🔒 Нет доступа. Отправьте /start')
        return
    items = Booking.objects.order_by('-id')[:10]
    if not items:
        reply(chat_id, 'Заявок пока нет.')
        return
    reply(chat_id, '\n\n'.join(
        f'<b>{escape(b.first_name)} {escape(b.last_name)}</b>\n'
        f'📞 {escape(b.phone)}\n💬 {escape(b.wish)}\n'
        f'📅 {b.date:%d.%m.%Y} {b.time:%H:%M}' for b in items))


def handle_logout(chat_id):
    deleted, _ = TelegramAdmin.objects.filter(chat_id=chat_id).delete()
    BotSession.objects.filter(chat_id=chat_id).update(awaiting_password=False)
    reply(chat_id, '👋 Вы вышли. Для входа отправьте /start' if deleted else 'Вы не были авторизованы.')


def process_update(update):
    message = update.get('message')
    if not message or 'text' not in message:
        return
    chat = message['chat']
    if chat.get('type') != 'private':
        return
    chat_id, user, text = chat['id'], message.get('from', {}), message['text']

    if text.startswith('/start'):
        handle_start(chat_id)
    elif text.startswith('/logout'):
        handle_logout(chat_id)
    elif text.startswith('/bookings'):
        handle_bookings(chat_id)
    else:
        session = BotSession.objects.filter(chat_id=chat_id).first()
        if session and session.awaiting_password:
            handle_password(chat_id, user, message['message_id'], text, session)
        elif not is_admin(chat_id):
            reply(chat_id, '🔒 Нет доступа. Отправьте /start')