from django.db import models


class TelegramRecipient(models.Model):
    chat_id = models.CharField(max_length=64, unique=True, verbose_name="Chat ID")
    first_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="First Name")
    username = models.CharField(max_length=150, blank=True, null=True, verbose_name="Username")
    is_active = models.BooleanField(default=True, verbose_name="ទទួលសារដំណឹង (Active)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Telegram Recipient'
        verbose_name_plural = 'Telegram Recipients'

    def __str__(self):
        label = self.first_name or self.username or "Recipient"
        return f"{label} ({self.chat_id})"
