from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import secrets
import string
from apps.services.models import LaundryService


def generate_order_code() -> str:
    """Generate 8-character unique order code: ORD-YYMMDD-XXXX"""
    date_str = timezone.now().strftime('%y%m%d')
    rand_chars = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    return f"ORD-{date_str}-{rand_chars}"


class Customer(models.Model):
    name = models.CharField(max_length=150, verbose_name='ឈ្មោះអតិថិជន (Customer Name)')
    phone = models.CharField(max_length=30, db_index=True, verbose_name='លេខទូរស័ព្ទ (Phone)')
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='អាសយដ្ឋាន (Address)')
    notes = models.TextField(blank=True, null=True, verbose_name='ចំណាំបន្ថែម (Notes)')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return f"{self.name} ({self.phone})"


class Order(models.Model):
    class Status(models.TextChoices):
        RECEIVED = 'RECEIVED', '1. ទទួល (Received)'
        WASHING = 'WASHING', '2. កំពុងបោក (Washing)'
        DRYING = 'DRYING', '3. កំពុងសម្ងួត (Drying)'
        IRONING = 'IRONING', '4. កំពុងអ៊ុត (Ironing)'
        READY = 'READY', '5. រួចរាល់ (Ready for Pickup)'
        COMPLETED = 'COMPLETED', '6. បានប្រគល់ (Completed)'
        CANCELLED = 'CANCELLED', 'បានបោះបង់ (Cancelled)'

    class PaymentStatus(models.TextChoices):
        UNPAID = 'UNPAID', 'មិនទាន់ទូទាត់ (Unpaid)'
        PARTIAL = 'PARTIAL', 'បង់មួយផ្នែក (Deposit / Partial)'
        PAID = 'PAID', 'ទូទាត់រួចរាល់ (Paid)'
        REFUNDED = 'REFUNDED', 'បានដកប្រាក់វិញ (Refunded)'

    class PaymentMethod(models.TextChoices):
        CASH = 'CASH', 'សាច់ប្រាក់ (Cash)'
        KHQR = 'KHQR', 'KHQR / Bakong Scan'
        TRANSFER = 'TRANSFER', 'ផ្ទេរប្រាក់តាមធនាគារ (Bank Transfer)'

    order_code = models.CharField(
        max_length=32,
        unique=True,
        db_index=True,
        default=generate_order_code,
        verbose_name='លេខកូដកញ្ចប់ (Order Code)'
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='អតិថិជន'
    )
    status = models.CharField(
        max_length=25,
        choices=Status.choices,
        default=Status.RECEIVED,
        db_index=True,
        verbose_name='ដំណាក់កាលបោកអ៊ុត'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
        db_index=True,
        verbose_name='ស្ថានភាពទូទាត់'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
        verbose_name='វិធីសាស្រ្តទូទាត់'
    )
    total_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='សរុបជាដុល្លារ ($)'
    )
    paid_amount_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='បានទូទាត់ ($)'
    )
    discount_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='បញ្ចុះតម្លៃ ($)'
    )
    exchange_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('4100.00'),
        verbose_name='អត្រាប្ដូរប្រាក់ (1$ = ៛)'
    )
    bag_count = models.PositiveIntegerField(
        default=1,
        verbose_name='ចំនួនស្បោង/កញ្ចប់ (Bag Count)'
    )
    is_express = models.BooleanField(
        default=False,
        verbose_name='សេវាបន្ទាន់ (Express)'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='ចំណាំលើការបោកអ៊ុត'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_orders',
        verbose_name='អ្នកបង្កើត'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"{self.order_code} - {self.customer.name} ({self.get_status_display()})"

    @property
    def total_khr(self) -> int:
        return int(self.total_usd * self.exchange_rate)

    @property
    def paid_amount_khr(self) -> int:
        return int(self.paid_amount_usd * self.exchange_rate)

    @property
    def balance_due_usd(self) -> Decimal:
        diff = self.total_usd - self.paid_amount_usd
        return max(Decimal('0.00'), diff)

    @property
    def balance_due_khr(self) -> int:
        return int(self.balance_due_usd * self.exchange_rate)

    def calculate_total(self):
        subtotal = sum(item.subtotal_usd for item in self.items.all())
        total = max(Decimal('0.00'), subtotal - self.discount_usd)
        self.total_usd = total
        if self.paid_amount_usd >= self.total_usd and self.total_usd > Decimal('0.00'):
            self.payment_status = self.PaymentStatus.PAID
        elif self.paid_amount_usd > Decimal('0.00'):
            self.payment_status = self.PaymentStatus.PARTIAL
        else:
            self.payment_status = self.PaymentStatus.UNPAID
        self.save(update_fields=['total_usd', 'payment_status', 'updated_at'])


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    service = models.ForeignKey(
        LaundryService,
        on_delete=models.PROTECT,
        verbose_name='សេវាកម្ម'
    )
    quantity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('1.00'),
        verbose_name='បរិមាណ (KG ឬ ចំនួនដុំ)'
    )
    unit_price_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='តម្លៃឯកតា ($)'
    )
    subtotal_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='សរុបរង ($)'
    )
    item_notes = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='ចំណាំខោអាវ (ឧ. អាវស, ស្លាកស្នាម)'
    )

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def save(self, *args, **kwargs):
        self.subtotal_usd = round(self.quantity * self.unit_price_usd, 2)
        super().save(*args, **kwargs)

    @property
    def subtotal_khr(self) -> int:
        return int(self.subtotal_usd * self.order.exchange_rate)
