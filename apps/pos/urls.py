from django.urls import path
from .views import (
    PosDashboardView,
    PosCreateOrderView,
    PosUpdateOrderStatusView,
    PosRecordPaymentView,
    PosOrderDetailView,
    ThermalReceiptView,
    LaundryTagView,
    CustomerLookupJsonView
)

app_name = 'pos'

urlpatterns = [
    path('', PosDashboardView.as_view(), name='dashboard'),
    path('order/create/', PosCreateOrderView.as_view(), name='create_order'),
    path('order/<int:pk>/', PosOrderDetailView.as_view(), name='order_detail'),
    path('order/<int:pk>/update-status/', PosUpdateOrderStatusView.as_view(), name='update_status'),
    path('order/<int:pk>/record-payment/', PosRecordPaymentView.as_view(), name='record_payment'),
    path('order/<int:pk>/receipt/', ThermalReceiptView.as_view(), name='thermal_receipt'),
    path('order/<int:pk>/tag/', LaundryTagView.as_view(), name='thermal_tag'),
    path('api/customers/lookup/', CustomerLookupJsonView.as_view(), name='customer_lookup'),
]
