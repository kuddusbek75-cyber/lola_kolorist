"""
Запуск бота: python manage.py run_bot
/start - запрос пароля, /bookings - последние заявки, /logout - выйти
"""
import hmac
import logging
import time
from html import escape

from django.conf import settings
from django.core.management.base import BaseCommand

from salon.models import Booking, TelegramAdmin
from salon.telegram_notify import call_api, send_telegram_message

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 5
BLOCK_SECONDS = 15 * 60
awaiting_password = set()
failed_attempts = {}  # chat_id -> (попытки, заблокирован до)

MENU = '/bookings - последние заявки\n/logout - выйти'


def is_admin(chat_id):
    return TelegramAdmin.objects.filter(chat_id=chat_id).exists()


def reply(chat_id, text):
    send_telegram_message(text, chat_id)


def handle_start(chat_id):
    if is_admin(chat_id):
        reply(chat_id, '✅ Вы авторизованы.\n\n' + MENU)
        return
    awaiting_password.add(chat_id)
    reply(chat_id, '🔒 Это закрытая CRM-система.\nВведите пароль:')


def handle_password(chat_id, user, message_id, text):
    count, blocked_until = failed_attempts.get(chat_id, (0, 0))
    if time.time() < blocked_until:
        reply(chat_id, f'⛔ Слишком много попыток. Повторите через {int((blocked_until - time.time()) // 60) + 1} мин.')
        return

    call_api('deleteMessage', {'chat_id': chat_id, 'message_id': message_id})

    expected = settings.ADMIN_PASSWORD
    if expected and hmac.compare_digest(text.strip().encode(), expected.encode()):
        TelegramAdmin.objects.update_or_create(chat_id=chat_id, defaults={
            'username': user.get('username', ''),
            'full_name': ' '.join(filter(None, [user.get('first_name'), user.get('last_name')])),
        })
        awaiting_password.discard(chat_id)
        failed_attempts.pop(chat_id, None)
        reply(chat_id, '✅ Доступ открыт. Новые заявки будут приходить сюда.\n\n' + MENU)
        logger.info('Админ авторизован: chat_id=%s', chat_id)
        return

    count += 1
    if count >= MAX_ATTEMPTS:
        failed_attempts[chat_id] = (0, time.time() + BLOCK_SECONDS)
        awaiting_password.discard(chat_id)
        reply(chat_id, '⛔ Доступ заблокирован на 15 минут.')
        logger.warning('Блокировка за перебор пароля: chat_id=%s', chat_id)
    else:
        failed_attempts[chat_id] = (count, 0)
        reply(chat_id, f'❌ Неверный пароль. Осталось попыток: {MAX_ATTEMPTS - count}')


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
    awaiting_password.discard(chat_id)
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
    elif chat_id in awaiting_password:
        handle_password(chat_id, user, message['message_id'], text)
    elif not is_admin(chat_id):
        reply(chat_id, '🔒 Нет доступа. Отправьте /start')


def poll_forever():
    """Бесконечный опрос Telegram. Используется и в run_bot, и в runserver."""
    offset = 0
    while True:
        data = call_api('getUpdates', {'timeout': 30, 'offset': offset}, timeout=(3, 40))
        if data is None:
            time.sleep(5)
            continue
        for update in data['result']:
            offset = update['update_id'] + 1
            try:
                process_update(update)
            except Exception:
                logger.exception('Ошибка обработки update')


class Command(BaseCommand):
    help = 'Запускает только Telegram-бота (обычно не нужно: бот стартует вместе с runserver)'

    def handle(self, *args, **options):
        if not settings.BOT_TOKEN or not settings.ADMIN_PASSWORD:
            self.stderr.write('Задайте BOT_TOKEN и ADMIN_PASSWORD в .env')
            return
        self.stdout.write('Бот запущен. Остановка: Ctrl+C')
        try:
            poll_forever()
        except KeyboardInterrupt:
            self.stdout.write('Остановлено.')
