from django.test import TestCase
from django.urls import reverse

class AccountsTests(TestCase):
    def test_login_page_renders(self):
        url = reverse('account_login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_signup_page_renders(self):
        url = reverse('account_signup')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
