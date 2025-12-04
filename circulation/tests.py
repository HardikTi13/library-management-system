from django.test import TestCase, Client
from django.urls import reverse
from .models import Book
import json

class BookApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('book-list-create')

    def test_create_and_list_books(self):
        # Test POST
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'isbn': '1234567890123',
            'category': 'Fiction'
        }
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Book.objects.filter(isbn='1234567890123').exists())

        # Test GET
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['title'], 'Test Book')
