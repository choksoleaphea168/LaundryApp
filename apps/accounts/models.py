from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        OWNER = 'OWNER', 'Owner / Manager (ម្ចាស់ហាង)'
        CASHIER = 'CASHIER', 'Cashier / POS (អ្នកគិតលុយ)'
        STAFF = 'STAFF', 'Laundry Staff (បុគ្គលិកបោកអ៊ុត)'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CASHIER,
        verbose_name='តួនាទី (Role)'
    )
    phone_number = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name='លេខទូរស័ព្ទ (Phone)'
    )

    def is_owner(self):
        return self.role == self.Role.OWNER or self.is_superuser

    def __str__(self):
        full_name = self.get_full_name()
        return f"{full_name} ({self.get_role_display()})" if full_name else f"{self.username} ({self.get_role_display()})"
