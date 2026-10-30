from django.core.management.base import BaseCommand
from decimal import Decimal
from apps.services.models import LaundryService, ServiceCategory, UnitType


class Command(BaseCommand):
    help = 'Seeds initial standard laundry services for Cambodia Laundry POS'

    def handle(self, *args, **options):
        services_data = [
            {
                'name': 'Wash & Fold Regular',
                'name_kh': 'បោកគក់ និងបត់ (ធម្មតា)',
                'category': ServiceCategory.WASH_FOLD,
                'unit_type': UnitType.PER_KG,
                'price_usd': Decimal('1.00'),
                'min_units': Decimal('1.00'),
                'estimated_hours': 24,
                'is_express': False
            },
            {
                'name': 'Wash & Ironing',
                'name_kh': 'បោកគក់ និងអ៊ុត',
                'category': ServiceCategory.WASH_FOLD,
                'unit_type': UnitType.PER_KG,
                'price_usd': Decimal('1.50'),
                'min_units': Decimal('1.00'),
                'estimated_hours': 24,
                'is_express': False
            },
            {
                'name': 'Express Wash & Fold',
                'name_kh': 'បោកគក់បន្ទាន់ (Express 4-6h)',
                'category': ServiceCategory.EXPRESS,
                'unit_type': UnitType.PER_KG,
                'price_usd': Decimal('2.00'),
                'min_units': Decimal('1.00'),
                'estimated_hours': 6,
                'is_express': True
            },
            {
                'name': 'Bedding & Blanket',
                'name_kh': 'កម្រាលពូក និងភួយ',
                'category': ServiceCategory.BEDDING,
                'unit_type': UnitType.PER_KG,
                'price_usd': Decimal('1.50'),
                'min_units': Decimal('2.00'),
                'estimated_hours': 48,
                'is_express': False
            },
            {
                'name': 'Suit / Blazer Dry Clean',
                'name_kh': 'បោកស្ងួត អាវធំ/ឈុត',
                'category': ServiceCategory.DRY_CLEAN,
                'unit_type': UnitType.PER_PIECE,
                'price_usd': Decimal('3.50'),
                'min_units': Decimal('1.00'),
                'estimated_hours': 48,
                'is_express': False
            },
            {
                'name': 'Shirt / Dress Ironing Only',
                'name_kh': 'អ៊ុតតែមួយមុខ (អាវ/រ៉ូប)',
                'category': ServiceCategory.IRONING_ONLY,
                'unit_type': UnitType.PER_PIECE,
                'price_usd': Decimal('0.50'),
                'min_units': Decimal('1.00'),
                'estimated_hours': 12,
                'is_express': False
            },
            {
                'name': 'Sneakers & Shoes Clean',
                'name_kh': 'បោកស្បែកជើង',
                'category': ServiceCategory.SPECIAL,
                'unit_type': UnitType.PER_PIECE,
                'price_usd': Decimal('2.50'),
                'min_units': Decimal('1.00'),
                'estimated_hours': 48,
                'is_express': False
            },
        ]

        count = 0
        for s in services_data:
            obj, created = LaundryService.objects.get_or_create(
                name=s['name'],
                defaults=s
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {count} laundry services!"))
