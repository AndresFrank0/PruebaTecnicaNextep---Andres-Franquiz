from django.db import IntegrityError, transaction
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from . import services
from .models import Book
from .serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    """CRUD de libros: la lista va paginada (ver REST_FRAMEWORK en settings)."""

    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def perform_create(self, serializer):
        self._save(serializer)

    def perform_update(self, serializer):
        self._save(serializer)

    @staticmethod
    def _save(serializer):
        """Guarda; si otra petición guardó el mismo ISBN entre la validación y el INSERT, responde 400."""
        try:
            # atomic: el IntegrityError no deja rota una transacción externa (ATOMIC_REQUESTS, tests).
            with transaction.atomic():
                serializer.save()
        except IntegrityError as exc:
            if 'isbn' not in str(exc):
                raise
            raise ValidationError({'isbn': ['Ya existe libro con este isbn.']}) from None

    def _paginated(self, queryset):
        """Responde con la misma forma paginada que GET /books."""
        page = self.paginate_queryset(queryset)
        return self.get_paginated_response(self.get_serializer(page, many=True).data)

    @action(detail=False)
    def search(self, request):
        """GET /books/search?category=... (coincidencia parcial, sin distinguir mayúsculas)."""
        category = request.query_params.get('category', '').strip()
        if not category:
            raise ValidationError({'category': 'Este parámetro es obligatorio.'})
        return self._paginated(self.get_queryset().filter(category__icontains=category))

    @action(detail=False, url_path='low-stock')
    def low_stock(self, request):
        """GET /books/low-stock?threshold=10: libros con stock_quantity <= threshold."""
        try:
            threshold = int(request.query_params.get('threshold', 10))
        except ValueError:
            raise ValidationError({'threshold': 'Debe ser un número entero.'}) from None
        return self._paginated(self.get_queryset().filter(stock_quantity__lte=threshold))

    # Serializer sin campos: el endpoint no lee el cuerpo, así que OPTIONS y la browsable API
    # no deben ofrecer el formulario de Book.
    @action(detail=True, methods=['post'], url_path='calculate-price', serializer_class=serializers.Serializer)
    def calculate_price(self, request, pk=None):
        """POST /books/{id}/calculate-price: precio de venta en Bs con la tasa BCV (se guarda en el libro)."""
        try:
            return Response(services.calculate_price(self.get_object()))
        except Book.DoesNotExist:  # lo borraron mientras se consultaba la API
            raise NotFound() from None
