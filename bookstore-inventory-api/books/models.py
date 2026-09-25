from decimal import Decimal

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

# El serializer normaliza el ISBN a solo dígitos antes de validar (ver serializers.py).
isbn_validator = RegexValidator(
    r'^(\d{9}[\dX]|\d{13})$', 'El ISBN debe tener 10 o 13 dígitos (se permiten guiones).'
)
country_validator = RegexValidator(
    r'^[A-Z]{2}$', 'Debe ser un código de país ISO de 2 letras (ej. ES).'
)


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True, validators=[isbn_validator])
    cost_usd = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))]
    )
    # Bolívares: 14 dígitos dejan margen para tasas de cambio altas.
    selling_price_local = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=100, db_index=True)
    supplier_country = models.CharField(max_length=2, validators=[country_validator])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'libro'

    def __str__(self):
        return self.title
