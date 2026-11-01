from django.contrib import admin

from .models import Booking, TelegramAdmin


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'wish', 'date', 'time', 'telegram_sent')
    list_filter = ('date', 'telegram_sent')
    search_fields = ('first_name', 'last_name', 'phone', 'wish')


@admin.register(TelegramAdmin)
class TelegramAdminAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'chat_id', 'created_at')
