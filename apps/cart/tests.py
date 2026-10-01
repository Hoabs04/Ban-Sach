from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.catalog.models import Book
from .models import Cart, CartItem

User = get_user_model()

class CartTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='cartuser@example.com',
            password='TestPassword123'
        )
        self.book = Book.objects.create(
            title='Test Book',
            slug='test-book',
            price=100000,
            stock=10
        )

    def test_add_to_cart_authenticated(self):
        self.client.force_login(self.user)
        url = reverse('cart:cart_add', args=[self.book.pk])
        response = self.client.post(url, {
            'quantity': 2,
            'next': reverse('cart:cart_detail')
        })
        self.assertEqual(response.status_code, 302)
        
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 1)
        item = cart.items.first()
        self.assertEqual(item.book, self.book)
        self.assertEqual(item.quantity, 2)

    def test_add_to_cart_exceed_stock(self):
        self.client.force_login(self.user)
        url = reverse('cart:cart_add', args=[self.book.pk])
        self.client.post(url, {
            'quantity': 15, # More than stock (10)
            'next': reverse('cart:cart_detail')
        })
        
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 0) # Should be rejected entirely

    def test_update_cart(self):
        self.client.force_login(self.user)
        cart = Cart.objects.create(user=self.user)
        item = CartItem.objects.create(cart=cart, book=self.book, quantity=2)
        
        url = reverse('cart:cart_update', args=[item.pk])
        self.client.post(url, {
            'quantity': 5
        })
        
        item.refresh_from_db()
        self.assertEqual(item.quantity, 5)

    def test_remove_from_cart(self):
        self.client.force_login(self.user)
        cart = Cart.objects.create(user=self.user)
        item = CartItem.objects.create(cart=cart, book=self.book, quantity=2)
        
        url = reverse('cart:cart_remove', args=[item.pk])
        self.client.post(url)
        
        self.assertEqual(cart.items.count(), 0)
