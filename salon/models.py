from django.db import models


class Booking(models.Model):
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    phone = models.CharField('Телефон', max_length=30)
    wish = models.CharField('Что нужно сделать', max_length=500, default='')
    date = models.DateField('Дата')
    time = models.TimeField('Время')
    telegram_sent = models.BooleanField('Отправлено в Telegram', default=False)
    created_at = models.DateTimeField('Создана', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'

    def __str__(self):
        return f'{self.first_name} {self.last_name} — {self.date} {self.time:%H:%M}'


class TelegramAdmin(models.Model):
    """Чаты, прошедшие авторизацию паролем в боте."""
    chat_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, blank=True)
    full_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Админ в Telegram'
        verbose_name_plural = 'Админы в Telegram'

    def __str__(self):
        return self.full_name or self.username or str(self.chat_id)


class BotSession(models.Model):
    """Состояние диалога с ботом. Хранится в базе, потому что на Vercel нет общей памяти."""
    chat_id = models.BigIntegerField(unique=True)
    awaiting_password = models.BooleanField(default=False)
    failed_count = models.PositiveIntegerField(default=0)
    blocked_until = models.DateTimeField(null=True, blank=True)