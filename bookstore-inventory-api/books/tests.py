from django.test import TestCase

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
