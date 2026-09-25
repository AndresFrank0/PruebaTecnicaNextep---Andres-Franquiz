from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APITestCase

from .models import Book
from .serializers import BookSerializer

VALID = {
    'title': 'El Quijote',
    'author': 'Miguel de Cervantes',
    'isbn': '978-84-376-0494-7',
    'cost_usd': 15.99,
    'stock_quantity': 25,
    'category': 'Literatura Clásica',
    'supplier_country': 'ES',
}


def make_book(**overrides):
    """Crea un libro directamente en la BD (sin pasar por el serializer)."""
    return Book.objects.create(**{**VALID, 'isbn': '9788437604947', **overrides})


class BookSerializerTests(TestCase):
    def errors_for(self, **overrides):
        serializer = BookSerializer(data={**VALID, **overrides})
        self.assertFalse(serializer.is_valid())
        return serializer.errors

    def test_valid_book_normalizes_isbn(self):
        serializer = BookSerializer(data=VALID)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['isbn'], '9788437604947')

    def test_cost_must_be_greater_than_zero(self):
        for cost in (0, -5):
            self.assertIn('cost_usd', self.errors_for(cost_usd=cost))

    def test_stock_cannot_be_negative(self):
        self.assertIn('stock_quantity', self.errors_for(stock_quantity=-1))

    def test_isbn_must_have_10_or_13_digits(self):
        for bad in ('123', '978-84-376-0494', 'abcdefghij', '12345678901234'):
            self.assertIn('isbn', self.errors_for(isbn=bad), bad)
        for good in ('0-306-40615-2', '123456789X'):
            self.assertTrue(BookSerializer(data={**VALID, 'isbn': good}).is_valid(), good)

    def test_duplicate_isbn_rejected_even_with_different_format(self):
        make_book()
        self.assertIn('isbn', self.errors_for(isbn='97-884-376-04947'))

    def test_supplier_country_must_be_iso2(self):
        self.assertIn('supplier_country', self.errors_for(supplier_country='ESP'))


class BookApiTests(APITestCase):
    def test_create_returns_201_without_selling_price(self):
        r = self.client.post('/books', VALID, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertIsNone(r.data['selling_price_local'])
        self.assertEqual(r.data['cost_usd'], Decimal('15.99'))

    def test_create_invalid_returns_400_with_field_errors(self):
        r = self.client.post('/books', {**VALID, 'cost_usd': 0, 'isbn': '123'}, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertIn('cost_usd', r.data)
        self.assertIn('isbn', r.data)

    def test_list_is_paginated(self):
        for i in range(12):
            make_book(isbn=f'{i:013d}')
        r = self.client.get('/books')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['count'], 12)
        self.assertEqual(len(r.data['results']), 10)
        self.assertIsNotNone(r.data['next'])

    def test_retrieve_existing_and_missing(self):
        book = make_book()
        self.assertEqual(self.client.get(f'/books/{book.id}').data['title'], 'El Quijote')
        self.assertEqual(self.client.get('/books/9999').status_code, 404)

    def test_update_ignores_selling_price(self):
        book = make_book()
        payload = {**VALID, 'stock_quantity': 3, 'selling_price_local': 999}
        r = self.client.put(f'/books/{book.id}', payload, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['stock_quantity'], 3)
        self.assertIsNone(r.data['selling_price_local'])

    def test_delete(self):
        book = make_book()
        self.assertEqual(self.client.delete(f'/books/{book.id}').status_code, 204)
        self.assertFalse(Book.objects.exists())


class BookFilterTests(APITestCase):
    def setUp(self):
        self.quijote = make_book()  # "Literatura Clásica", stock 25
        self.low = make_book(isbn='0306406152', title='Cosmos', category='Ciencia', stock_quantity=2)

    def test_search_by_category_is_partial_and_case_insensitive(self):
        r = self.client.get('/books/search', {'category': 'literatura'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual([b['id'] for b in r.data['results']], [self.quijote.id])

    def test_search_requires_category(self):
        self.assertEqual(self.client.get('/books/search').status_code, 400)

    def test_low_stock_uses_threshold(self):
        r = self.client.get('/books/low-stock', {'threshold': 10})
        self.assertEqual([b['id'] for b in r.data['results']], [self.low.id])
        self.assertEqual(self.client.get('/books/low-stock', {'threshold': 30}).data['count'], 2)

    def test_low_stock_rejects_non_integer_threshold(self):
        self.assertEqual(self.client.get('/books/low-stock', {'threshold': 'abc'}).status_code, 400)
