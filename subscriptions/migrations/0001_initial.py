# Generated by Django 5.1.4 on 2024-12-17 08:55

import django.core.validators
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(db_index=True, max_length=100)),
                ('description', models.TextField(blank=True)),
                ('price', models.DecimalField(db_index=True, decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('duration_months', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(60)])),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('active', 'Active'), ('expired', 'Expired'), ('failed', 'Failed')], db_index=True, default='pending', max_length=20)),
            ],
            options={
                'ordering': ['price'],
                'indexes': [models.Index(fields=['price', 'status'], name='subscriptio_price_7cae4b_idx'), models.Index(fields=['status', 'duration_months'], name='subscriptio_status_c6fc54_idx')],
            },
        ),
    ]