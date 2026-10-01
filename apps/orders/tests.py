from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.catalog.models import Book
from apps.cart.models import Cart, CartItem
from .models import Order, OrderItem, Coupon

User = get_user_model()

class OrderTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='orderuser@example.com',
            password='TestPassword123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2', email='orderuser2@example.com',
            password='TestPassword123'
        )
        self.book = Book.objects.create(
            title='Test Book',
            slug='test-book',
            price=100000,
            stock=10,
            sold_count=2
        )
        
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            book=self.book,
            quantity=2
        )

        self.coupon = Coupon.objects.create(
            code='DISCOUNT10',
            discount_type=Coupon.DiscountType.PERCENTAGE,
            discount_value=10,
            valid_from=timezone.now() - timedelta(days=1),
            valid_to=timezone.now() + timedelta(days=1),
            usage_limit=1,
            used_count=0,
            is_active=True
        )

    def test_checkout_creates_order(self):
        self.client.force_login(self.user)
        url = reverse('orders:checkout')
        response = self.client.post(url, {
            'shipping_name': 'Test Name',
            'shipping_phone': '0123456789',
            'shipping_address': '123 Test St',
            'shipping_district': 'Test District',
            'shipping_city': 'Test City',
            'payment_method': 'cod',
        })
        self.assertEqual(response.status_code, 302)
        
        # Check order created
        order = Order.objects.filter(user=self.user).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.items.count(), 1)
        
        # Check stock reduced
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock, 8)
        self.assertEqual(self.book.sold_count, 4)
        
        # Check cart cleared
        self.assertEqual(self.cart.items.count(), 0)

    def test_checkout_with_coupon(self):
        self.client.force_login(self.user)
        url = reverse('orders:checkout')
        response = self.client.post(url, {
            'shipping_name': 'Test Name',
            'shipping_phone': '0123456789',
            'shipping_address': '123 Test St',
            'shipping_district': 'Test District',
            'shipping_city': 'Test City',
            'payment_method': 'cod',
            'coupon_code': 'DISCOUNT10'
        })
        self.assertEqual(response.status_code, 302)
        
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.coupon, self.coupon)
        self.assertEqual(order.discount_amount, 20000) # 10% of 200,000
        
        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.used_count, 1)

    def test_order_cancel_restores_stock(self):
        self.client.force_login(self.user)
        order = Order.objects.create(
            user=self.user,
            order_number='TEST001',
            shipping_name='Test Name',
            shipping_phone='0123456789',
            shipping_address='123 Test St',
            shipping_district='Test District',
            shipping_city='Test City',
            subtotal=200000,
            shipping_fee=30000,
            discount_amount=0,
            total=230000,
            payment_method='cod',
            status=Order.Status.PENDING
        )
        OrderItem.objects.create(
            order=order,
            book=self.book,
            book_title=self.book.title,
            book_price=self.book.price,
            quantity=2
        )
        
        url = reverse('orders:order_cancel', args=[order.order_number])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CANCELLED)
        
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock, 12) # 10 + 2
        self.assertEqual(self.book.sold_count, 0) # 2 - 2 = 0

    def test_other_user_cannot_view_order(self):
        order = Order.objects.create(
            user=self.user,
            order_number='TEST002',
            shipping_name='Test Name',
            shipping_phone='0123456789',
            shipping_address='123 Test St',
            shipping_district='Test District',
            shipping_city='Test City',
            subtotal=200000,
            shipping_fee=30000,
            discount_amount=0,
            total=230000,
            payment_method='cod',
            status=Order.Status.PENDING
        )
        
        self.client.force_login(self.user2)
        url = reverse('orders:order_detail', args=[order.order_number])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
