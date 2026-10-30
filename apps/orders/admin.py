from django.contrib import admin
from .models import Customer, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ('service', 'quantity', 'unit_price_usd', 'subtotal_usd', 'item_notes')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'address', 'created_at')
    search_fields = ('name', 'phone')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_code', 'customer', 'status', 'payment_status',
        'total_usd', 'paid_amount_usd', 'is_express', 'created_at'
    )
    list_filter = ('status', 'payment_status', 'payment_method', 'is_express', 'created_at')
    search_fields = ('order_code', 'customer__name', 'customer__phone')
    inlines = [OrderItemInline]
