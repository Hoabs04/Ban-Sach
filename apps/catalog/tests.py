from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Book, Category, Review

User = get_user_model()

class CatalogTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com',
            password='TestPassword123'
        )
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.book = Book.objects.create(
            title='Test Book',
            slug='test-book',
            price=100000,
            stock=10
        )
        self.book.categories.add(self.category)

    def test_add_review_valid(self):
        self.client.force_login(self.user)
        url = reverse('catalog:add_review', args=[self.book.slug])
        response = self.client.post(url, {
            'rating': '4',
            'title': 'Great Book',
            'comment': 'I really loved this book.'
        })
        self.assertEqual(response.status_code, 302)
        review = Review.objects.filter(book=self.book, user=self.user).first()
        self.assertIsNotNone(review)
        self.assertEqual(review.rating, 4)

    def test_add_review_invalid_rating_high(self):
        self.client.force_login(self.user)
        url = reverse('catalog:add_review', args=[self.book.slug])
        response = self.client.post(url, {
            'rating': '9',
            'title': 'Bad Rating',
            'comment': 'Rating is out of bounds.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.filter(book=self.book, user=self.user).exists())

    def test_add_review_invalid_rating_type(self):
        self.client.force_login(self.user)
        url = reverse('catalog:add_review', args=[self.book.slug])
        response = self.client.post(url, {
            'rating': 'abc',
            'title': 'Bad Rating Type',
            'comment': 'Rating is not a number.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.filter(book=self.book, user=self.user).exists())

    def test_filter_invalid_query_params(self):
        url = reverse('catalog:book_list')
        response = self.client.get(url, {'min_price': 'abc', 'rating': 'xyz'})
        self.assertEqual(response.status_code, 200) # Should not 500
