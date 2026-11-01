from django.urls import path

from . import views
from .webhook import telegram_webhook

urlpatterns = [
    path('', views.index, name='index'),
    path('spasibo/', views.success, name='success'),
    path('tg/webhook/', telegram_webhook),
]