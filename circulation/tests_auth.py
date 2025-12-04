from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
import json

class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')
        self.signin_url = reverse('signin')
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword123',
            'email': 'test@example.com'
        }

    def test_signup(self):
        response = self.client.post(
            self.signup_url,
            json.dumps(self.user_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_signup_duplicate_username(self):
        User.objects.create_user(**self.user_data)
        response = self.client.post(
            self.signup_url,
            json.dumps(self.user_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_signin_success(self):
        User.objects.create_user(**self.user_data)
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post(
            self.signin_url,
            json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_signin_invalid_credentials(self):
        User.objects.create_user(**self.user_data)
        login_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(
            self.signin_url,
            json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
