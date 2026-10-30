from django.core.management.base import BaseCommand
from decimal import Decimal
from django.utils import timezone
from apps.accounts.models import User
from apps.orders.models import Customer, Order, OrderItem
from apps.services.models import LaundryService


class Command(BaseCommand):
    help = 'Seeds sample laundry orders for POS testing'

    def handle(self, *args, **options):
        # 1. Customers
        c1, _ = Customer.objects.get_or_create(phone='012888999', defaults={'name': 'សុខ ចាន់ដា', 'address': 'ទួលគោក, ភ្នំពេញ'})
        c2, _ = Customer.objects.get_or_create(phone='098777666', defaults={'name': 'រ័ត្ន វិសាល', 'address': 'បឹងកេងកង, ភ្នំពេញ'})
        c3, _ = Customer.objects.get_or_create(phone='077555444', defaults={'name': 'គឹម សៀវម៉ី', 'address': 'សែនសុខ, ភ្នំពេញ'})

        s_wash = LaundryService.objects.filter(category='WASH_FOLD').first()
        s_iron = LaundryService.objects.filter(category='IRONING_ONLY').first()
        s_bed = LaundryService.objects.filter(category='BEDDING').first()
        s_suit = LaundryService.objects.filter(category='DRY_CLEAN').first()

        admin_user = User.objects.filter(username='admin').first()

        # Order 1: Received
        o1 = Order.objects.create(
            customer=c1,
            status=Order.Status.RECEIVED,
            bag_count=1,
            is_express=False,
            notes='បោកថ្នម កុំដាក់ម្សៅក្រអូបខ្លាំង',
            payment_method=Order.PaymentMethod.CASH,
            created_by=admin_user
        )
        if s_wash:
            OrderItem.objects.create(order=o1, service=s_wash, quantity=Decimal('3.50'), unit_price_usd=s_wash.price_usd)
        o1.calculate_total()

        # Order 2: Washing
        o2 = Order.objects.create(
            customer=c2,
            status=Order.Status.WASHING,
            bag_count=2,
            is_express=True,
            notes='សេវាប្រញាប់ យកថ្ងៃនេះ',
            paid_amount_usd=Decimal('6.00'),
            payment_method=Order.PaymentMethod.KHQR,
            created_by=admin_user
        )
        if s_wash:
            OrderItem.objects.create(order=o2, service=s_wash, quantity=Decimal('4.00'), unit_price_usd=s_wash.price_usd)
        if s_suit:
            OrderItem.objects.create(order=o2, service=s_suit, quantity=Decimal('1.00'), unit_price_usd=s_suit.price_usd)
        o2.calculate_total()

        # Order 3: Ready for pickup
        o3 = Order.objects.create(
            customer=c3,
            status=Order.Status.READY,
            bag_count=1,
            is_express=False,
            notes='អ៊ុតរួចរាល់ ព្យួរអាវ',
            paid_amount_usd=Decimal('3.00'),
            payment_method=Order.PaymentMethod.CASH,
            ready_at=timezone.now(),
            created_by=admin_user
        )
        if s_bed:
            OrderItem.objects.create(order=o3, service=s_bed, quantity=Decimal('2.00'), unit_price_usd=s_bed.price_usd)
        o3.calculate_total()

        self.stdout.write(self.style.SUCCESS("Sample orders created successfully!"))
