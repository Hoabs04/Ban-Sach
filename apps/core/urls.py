from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('shipping-policy/', views.shipping_policy, name='shipping_policy'),
    path('return-policy/', views.return_policy, name='return_policy'),
    path('terms/', views.terms, name='terms'),
    path('newsletter/', views.newsletter_subscribe, name='newsletter_subscribe'),
]
