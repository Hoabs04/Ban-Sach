from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('success/<str:order_number>/', views.order_success, name='order_success'),
    path('detail/<str:order_number>/', views.order_detail, name='order_detail'),
    path('cancel/<str:order_number>/', views.order_cancel, name='order_cancel'),
    path('vnpay_return/', views.vnpay_return, name='vnpay_return'),
]
