# Generated by Django 5.1.4 on 2024-12-27 18:21

import django.core.validators
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(db_index=True, help_text='Shop name', max_length=255)),
                ('address', models.CharField(help_text='Physical address of the shop', max_length=255)),
                ('phone_number', models.CharField(help_text='Contact phone number', max_length=15, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+8801234567890'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')])),
                ('email', models.EmailField(help_text='Contact email address', max_length=255)),
                ('return_policy', models.TextField(help_text="Shop's return policy")),
                ('website', models.URLField(blank=True, help_text="Shop's website URL", null=True)),
                ('shop_logo', models.ImageField(blank=True, help_text='Recommended size: 300x300 pixels. Maximum file size: 1MB. Images will be automatically resized if larger. Supported formats: JPG, JPEG, PNG', null=True, upload_to='shops/logos/')),
                ('is_active', models.BooleanField(default=True, help_text='Whether the shop is currently active')),
                ('employees', models.ManyToManyField(blank=True, related_name='employed_at', to=settings.AUTH_USER_MODEL, verbose_name='Shop Employees')),
                ('owner', models.ManyToManyField(related_name='owned_shops', to=settings.AUTH_USER_MODEL, verbose_name='Shop Owners')),
            ],
            options={
                'verbose_name': 'Shop',
                'verbose_name_plural': 'Shops',
                'indexes': [models.Index(fields=['name'], name='shops_shop_name_da338f_idx'), models.Index(fields=['name', 'address'], name='shops_shop_name_1c5bf0_idx')],
            },
        ),
    ]
