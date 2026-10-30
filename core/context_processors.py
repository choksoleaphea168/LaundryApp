from django.conf import settings


def currency_and_shop_info(request):
    """Context processor providing shop info and currency exchange rate to all templates."""
    return {
        'SHOP_NAME': getattr(settings, 'SHOP_NAME', 'Smart Clean Laundry'),
        'SHOP_NAME_KH': getattr(settings, 'SHOP_NAME_KH', 'ហាងបោកអ៊ុត ស្មាតឃ្លីន'),
        'SHOP_PHONE': getattr(settings, 'SHOP_PHONE', '012 345 678'),
        'SHOP_ADDRESS': getattr(settings, 'SHOP_ADDRESS', 'Phnom Penh'),
        'SHOP_ADDRESS_KH': getattr(settings, 'SHOP_ADDRESS_KH', 'ភ្នំពេញ'),
        'EXCHANGE_RATE': getattr(settings, 'EXCHANGE_RATE_USD_TO_KHR', 4100),
        'DEFAULT_CURRENCY': getattr(settings, 'DEFAULT_CURRENCY', 'USD'),
    }
