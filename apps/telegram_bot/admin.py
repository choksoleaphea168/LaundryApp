from django.contrib import admin
from .models import TelegramRecipient


@admin.register(TelegramRecipient)
class TelegramRecipientAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'first_name', 'username', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('chat_id', 'first_name', 'username')
