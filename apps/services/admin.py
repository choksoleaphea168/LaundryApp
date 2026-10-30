from django.contrib import admin
from .models import LaundryService


@admin.register(LaundryService)
class LaundryServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_kh', 'category', 'unit_type', 'price_usd', 'price_khr_display', 'is_active')
    list_filter = ('category', 'unit_type', 'is_active', 'is_express')
    search_fields = ('name', 'name_kh')

    def price_khr_display(self, obj):
        return f"{obj.price_khr:,} ៛"
    price_khr_display.short_description = 'តម្លៃជារៀល (KHR)'
