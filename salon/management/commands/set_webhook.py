import json

from django.conf import settings
from django.core.management.base import BaseCommand

from salon.telegram_notify import call_api


class Command(BaseCommand):
    help = 'Регистрирует webhook: python manage.py set_webhook https://ваш-сайт.vercel.app'

    def add_arguments(self, parser):
        parser.add_argument('base_url')

    def handle(self, *args, **options):
        if not settings.BOT_TOKEN or not settings.TELEGRAM_WEBHOOK_SECRET:
            self.stderr.write('Задайте BOT_TOKEN и TELEGRAM_WEBHOOK_SECRET в .env')
            return
        url = options['base_url'].rstrip('/') + '/tg/webhook/'
        result = call_api('setWebhook', {
            'url': url,
            'secret_token': settings.TELEGRAM_WEBHOOK_SECRET,
            'allowed_updates': json.dumps(['message']),
            'drop_pending_updates': 'true',
        })
        self.stdout.write(f'Webhook установлен: {url}' if result else 'Ошибка, смотрите лог выше.')