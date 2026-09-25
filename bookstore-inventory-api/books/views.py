from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from .models import Book
from .serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    """CRUD de libros: la lista va paginada (ver REST_FRAMEWORK en settings)."""

    queryset = Book.objects.all()
    serializer_class = BookSerializer

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
            raise ValidationError({'threshold': 'Debe ser un número entero.'})
        return self._paginated(self.get_queryset().filter(stock_quantity__lte=threshold))
