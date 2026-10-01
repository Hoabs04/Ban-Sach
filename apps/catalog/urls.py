from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('search/', views.book_search, name='book_search'),
    path('category/<str:slug>/', views.category_detail, name='category_detail'),
    path('author/<str:slug>/', views.author_detail, name='author_detail'),
    path('book/<str:slug>/', views.book_detail, name='book_detail'),
    path('book/<str:slug>/review/', views.add_review, name='add_review'),
]
