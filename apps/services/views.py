from django.http import JsonResponse
from django.views import View
from .models import LaundryService


class ServiceListJsonView(View):
    def get(self, request, *args, **kwargs):
        services = LaundryService.objects.filter(is_active=True).values(
            'id', 'name', 'name_kh', 'category', 'unit_type', 'price_usd', 'min_units', 'is_express'
        )
        data = []
        for s in services:
            item = dict(s)
            item['price_usd'] = float(s['price_usd'])
            item['min_units'] = float(s['min_units'])
            data.append(item)
        return JsonResponse({'services': data})
