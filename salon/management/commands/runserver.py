"""
python manage.py runserver — одна команда делает всё:
  1) применяет миграции (создаёт базу и услуги),
  2) создаёт администратора сайта из .env (если его ещё нет),
  3) запускает Telegram-бота в фоне,
  4) поднимает сайт.
"""
import logging
import os
import threading

from django.conf import settings
from django.contrib.staticfiles.management.commands.runserver import Command as BaseRunserver
from django.core.management import call_command

logger = logging.getLogger(__name__)


def ensure_site_admin(stdout):
    from django.contrib.auth import get_user_model
    username = os.getenv('DJANGO_ADMIN_USER')
    password = os.getenv('DJANGO_ADMIN_PASSWORD')
    if not username or not password:
        return
    User = get_user_model()
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, '', password)
        stdout.write(f'Создан администратор сайта: {username}')


def start_bot(stdout):
    if not settings.BOT_TOKEN or not settings.ADMIN_PASSWORD:
        stdout.write('Бот не запущен: задайте BOT_TOKEN и ADMIN_PASSWORD в .env')
        return
    from .run_bot import poll_forever
    threading.Thread(target=poll_forever, name='telegram-bot', daemon=True).start()
    stdout.write('Telegram-бот запущен вместе с сайтом.')


class Command(BaseRunserver):
    def inner_run(self, *args, **options):
        # inner_run выполняется один раз в рабочем процессе (не в процессе-наблюдателе)
        call_command('migrate', interactive=False, verbosity=0)
        ensure_site_admin(self.stdout)
        start_bot(self.stdout)
        super().inner_run(*args, **options)
