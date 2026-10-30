from django.db import models
from django.conf import settings
from decimal import Decimal


class ServiceCategory(models.TextChoices):
    WASH_FOLD = 'WASH_FOLD', 'Wash & Fold (បោកគក់ និងបត់)'
    DRY_CLEAN = 'DRY_CLEAN', 'Dry Clean (បោកស្ងួត)'
    IRONING_ONLY = 'IRONING_ONLY', 'Ironing Only (អ៊ុតតែមួយមុខ)'
    BEDDING = 'BEDDING', 'Bedding & Curtains (កម្រាលពូក និងភួយ)'
    EXPRESS = 'EXPRESS', 'Express Priority (សេវាបន្ទាន់)'
    SPECIAL = 'SPECIAL', 'Shoes & Bags (ស្បែកជើង និងកាបូប)'


class UnitType(models.TextChoices):
    PER_KG = 'PER_KG', 'Per Kilogram / គិតជាគីឡូ (KG)'
    PER_PIECE = 'PER_PIECE', 'Per Piece / គិតជារាយដុំ (Pcs)'


class LaundryService(models.Model):
    name = models.CharField(max_length=120, verbose_name='ឈ្មោះសេវាកម្ម (Service Name)')
    name_kh = models.CharField(max_length=150, blank=True, verbose_name='ឈ្មោះជាភាសាខ្មែរ (Khmer Name)')
    category = models.CharField(
        max_length=30,
        choices=ServiceCategory.choices,
        default=ServiceCategory.WASH_FOLD,
        verbose_name='ប្រភេទសេវា'
    )
    unit_type = models.CharField(
        max_length=20,
        choices=UnitType.choices,
        default=UnitType.PER_KG,
        verbose_name='វិធីគិតថ្លៃ (Unit Type)'
    )
    price_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='តម្លៃជាដុល្លារ ($ USD)'
    )
    min_units = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('1.00'),
        verbose_name='បរិមាណអប្បបរមា (Min Units)'
    )
    estimated_hours = models.PositiveIntegerField(
        default=24,
        verbose_name='រយៈពេលប៉ាន់ស្មាន (ម៉ោង)'
    )
    is_express = models.BooleanField(
        default=False,
        verbose_name='សេវាបន្ទាន់ (Express)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='បើកដំណើរការ'
    )

    class Meta:
        ordering = ['category', 'name']
        verbose_name = 'Laundry Service'
        verbose_name_plural = 'Laundry Services'

    def __str__(self):
        display_name = f"{self.name} ({self.name_kh})" if self.name_kh else self.name
        unit = "kg" if self.unit_type == UnitType.PER_KG else "pcs"
        return f"{display_name} - ${self.price_usd}/{unit}"

    @property
    def price_khr(self) -> int:
        exchange_rate = getattr(settings, 'EXCHANGE_RATE_USD_TO_KHR', Decimal('4100'))
        return int(self.price_usd * exchange_rate)
