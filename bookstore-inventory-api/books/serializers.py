import re

from rest_framework import serializers

from .models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'
        read_only_fields = ['selling_price_local', 'created_at', 'updated_at']

    def to_internal_value(self, data):
        # Se normaliza antes de los validadores del campo, así la validación de unicidad
        # trata "978-84-..." y "97884..." como el mismo ISBN.
        if isinstance(data, dict) and isinstance(data.get('isbn'), str):
            data = data.copy()
            data['isbn'] = re.sub(r'[\s-]', '', data['isbn']).upper()
        return super().to_internal_value(data)
