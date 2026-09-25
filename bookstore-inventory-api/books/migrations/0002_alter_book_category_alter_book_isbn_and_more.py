# Generada por Django 5.2.17 el 2026-09-25 17:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='category',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='book',
            name='isbn',
            field=models.CharField(max_length=13, unique=True, validators=[django.core.validators.RegexValidator('^([0-9]{9}[0-9X]|[0-9]{13})\\Z', 'El ISBN debe tener 10 o 13 dígitos.')]),
        ),
        migrations.AlterField(
            model_name='book',
            name='selling_price_local',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
    ]
