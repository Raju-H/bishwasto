from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from accounts.models import BaseModel
from decimal import Decimal
from PIL import Image
from shops.models import Shop






class ProductCategory(BaseModel):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='createdby_categories'
    )
    is_active = models.BooleanField(default=True)

 
    class Meta:
        verbose_name_plural = 'Product categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"





class ProductSubCategory(BaseModel):
    category = models.ForeignKey(
        ProductCategory, 
        on_delete=models.CASCADE,
        related_name='subcategories'
    )
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='createdby_subcategories'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Product subcategories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.category.name}"







class Product(BaseModel):
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name='cat_products'
    )
    sub_category = models.ForeignKey(
        ProductSubCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcat_products'
    )
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    sku = models.CharField(max_length=255, blank=True, null=True)
    isbn = models.CharField(max_length=255, blank=True, null=True)
    variant = models.CharField(max_length=255, blank=True, null=True)
    is_expirable = models.BooleanField(default=False)
    expiry_date = models.DateField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='createdby_products'
    )
    WEIGHT_UNITS = (
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('lb', 'Pound'),
        ('oz', 'Ounce'),
        ('mg', 'Milligram'),
        ('t', 'Ton'),
        ('lt', 'Liter'),
        ('ml', 'Milliliter'),
        ('gal', 'Gallon')
    )
    weight_unit = models.CharField(
        max_length=3,
        choices=WEIGHT_UNITS,
        default='kg',
        blank=True,
        null=True
        )
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        blank=True,
        null=True
        )
    LENGTH_UNITS = (
        ('m', 'Meter'),
        ('cm', 'Centimeter'),
        ('in', 'Inch'),
        ('ft', 'Feet'),
        ('yd', 'Yard'),
        ('mm', 'Millimeter')
    )
    length_unit = models.CharField(
        max_length=2,
        choices=LENGTH_UNITS,
        default='cm',
        blank=True,
        null=True
        )
    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        blank=True,
        null=True
        )
    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        blank=True,
        null=True
        )
    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        blank=True,
        null=True
        )
    avatar = models.ImageField(
        upload_to='products/avatars/%Y/%m/',
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=True)


    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name', 'slug']),
            models.Index(fields=['category', 'is_active']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        if self.avatar:
            img = Image.open(self.avatar.path)
            if img.resize((300, 300), Image.LANCZOS):
                img.save(self.avatar.path)

    def __str__(self):
        return f"{self.name}"






class ShopProduct(BaseModel):
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='shop_shopproducts'
    )
    supplier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supplied_products'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='shop_products'
    )
    buying_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    wholesale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        null=True,
        blank=True
    )
    retail_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    receivings_stock = models.PositiveIntegerField(default=0)
    sort_order = models.PositiveIntegerField(default=0)
    stock_warning_threshold = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Percentage of reorder level at which stock is considered low"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='createdby_shopproducts'
    )
    qrcode = models.ImageField(
    upload_to='products/qrcodes/%Y/%m/',
    null=True,
    blank=True)
    default_tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=0
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Shop products'

    def clean(self):
        if self.stock_quantity < 0:
            raise ValueError("Stock quantity cannot be negative.")
        if self.receivings_stock < 0:
            raise ValueError("Receivings stock cannot be negative.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.shop.name}"
    

    def to_json(self):
        item = {
            'id': self.id,
            'name': self.product.name if self.product else None,
            'slug': self.product.slug if self.product else None,
            'category': self.product.category.name if self.product and self.product.category else None,
            'sub_category': self.product.sub_category.name if self.product and self.product.sub_category else None,
            'stock_quantity': self.stock_quantity,
            'avatar': self.product.avatar.url if self.product and self.product.avatar else None,
            'buying_price': self.buying_price,
            'wholesale_price': self.wholesale_price,
            'retail_price': self.retail_price,
            'default_tax_rate': self.default_tax_rate,
        }
        return item



        