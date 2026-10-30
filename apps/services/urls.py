from django.urls import path
from .views import ServiceListJsonView

app_name = 'services'

urlpatterns = [
    path('api/list/', ServiceListJsonView.as_view(), name='api_list'),
]
