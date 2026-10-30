from django.urls import path
from .views import OrderPublicTrackingView

app_name = 'orders'

urlpatterns = [
    path('track/<str:order_code>/', OrderPublicTrackingView.as_view(), name='track_order'),
]
