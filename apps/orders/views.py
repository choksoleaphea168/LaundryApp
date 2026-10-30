from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Order


class OrderPublicTrackingView(View):
    """Public customer tracking page via QR Code or direct link."""
    def get(self, request, order_code, *args, **kwargs):
        order = get_object_or_404(
            Order.objects.select_related('customer').prefetch_related('items__service'),
            order_code=order_code
        )
        return render(request, 'orders/tracking.html', {'order': order})
