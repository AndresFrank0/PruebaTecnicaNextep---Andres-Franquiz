from rest_framework import viewsets

from .models import Book
from .serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    """CRUD de libros: la lista va paginada (ver REST_FRAMEWORK en settings)."""

    queryset = Book.objects.all()
    serializer_class = BookSerializer
