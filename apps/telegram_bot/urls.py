from django.urls import path
from .views import TelegramWebhookView, sync_telegram_updates

app_name = 'telegram_bot'

urlpatterns = [
    path('webhook/', TelegramWebhookView.as_view(), name='webhook'),
    path('sync/', sync_telegram_updates, name='sync'),
]
