from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from accounts.models import BaseModel
from decimal import Decimal
from PIL import Image
from shops.models import Shop
from django.forms import model_to_dict

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



        




# class Product(BaseModel):
#     shop = models.ForeignKey(
#         Shop, 
#         on_delete=models.CASCADE,
#         related_name='shop_products'
#     )
#     supplier = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='supplied_products'
#     )
#     category = models.ForeignKey(
#         ProductCategory,
#         on_delete=models.CASCADE,
#         related_name='cat_products'
#     )
#     sub_category = models.ForeignKey(
#         ProductSubCategory,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='subcat_products'
#     )
#     name = models.CharField(max_length=255, db_index=True)
#     slug = models.SlugField(max_length=255, unique=True)
#     description = models.TextField(blank=True)
#     avatar = models.ImageField(
#         upload_to='products/avatars/%Y/%m/',
#         null=True,
#         blank=True
#     )
#     buying_price = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         validators=[MinValueValidator(Decimal('0.00'))]
#     )
#     wholesale_price = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         validators=[MinValueValidator(Decimal('0.00'))]
#     )
#     retail_price = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         validators=[MinValueValidator(Decimal('0.00'))]
#     )
#     stock_quantity = models.PositiveIntegerField(default=0)
#     receivings_stock = models.PositiveIntegerField(default=0)
#     sort_order = models.PositiveIntegerField(default=0)
#     stock_warning_threshold = models.PositiveIntegerField(
#         default=10,
#         validators=[MinValueValidator(1), MaxValueValidator(100)],
#         help_text="Percentage of reorder level at which stock is considered low"
#     )
#     is_active = models.BooleanField(default=True)


#     class Meta:
#         ordering = ['name']
#         indexes = [
#             models.Index(fields=['name', 'slug']),
#             models.Index(fields=['shop', 'category', 'is_active']),
#             models.Index(fields=['stock_quantity', 'receivings_stock']),
#         ]

#     def clean(self):
#         if self.wholesale_price < self.buying_price:
#             raise ValidationError("Wholesale price cannot be less than buying price")
#         if self.retail_price < self.wholesale_price:
#             raise ValidationError("Retail price cannot be less than wholesale price")

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.name)
#         self.full_clean()
#         self._invalidate_cache()
#         super().save(*args, **kwargs)

#     def _invalidate_cache(self):
#         cache_keys = [
#             f'product_{self.id}',
#             f'shop_products_{self.shop_id}',
#             f'category_products_{self.category_id}'
#         ]
#         cache.delete_many(cache_keys)

#     @property
#     def profit_margin(self):
#         """Calculate profit margin percentage."""
#         return ((self.retail_price - self.buying_price) / self.buying_price) * 100
    
#     @property
#     def stock_status(self):
#         """
#         Returns the current stock status.
#         Returns: 'out_of_stock', 'critical', 'low', or 'normal'
#         """
#         if self.stock_quantity == 0:
#             return 'out_of_stock'
        
#         threshold_qty = self.receivings_stock * (1 + self.stock_warning_threshold/100)
        
#         if self.stock_quantity <= self.receivings_stock:
#             return 'critical'
#         elif self.stock_quantity <= threshold_qty:
#             return 'low'
#         return 'normal'
    

#     @property
#     def stock_level_percentage(self):
#         """Returns stock level as percentage of reorder level."""
#         if self.receivings_stock == 0:
#             return 100
#         return (self.stock_quantity / self.receivings_stock) * 100

#     def needs_reorder(self):
#         """
#         Determines if product needs reordering based on:
#         - Current stock quantity
#         - Reorder level
#         - Average daily sales (if implemented)
#         """
#         return self.stock_quantity <= self.receivings_stock

#     def __str__(self):
#         return f"{self.name} - {self.shop.name}"


# class ProductImage(BaseModel):
#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE,
#         related_name='images'
#     )
#     image = models.ImageField(
#         upload_to='products/images/%Y/%m/',
#         help_text="Product image"
#     )
#     is_primary = models.BooleanField(default=False)
#     alt_text = models.CharField(max_length=255, blank=True)
#     order = models.PositiveIntegerField(default=0)

#     class Meta:
#         ordering = ['order', '-is_primary']
#         indexes = [
#             models.Index(fields=['product', 'is_primary']),
#         ]

#     def save(self, *args, **kwargs):
#         if self.is_primary:
#             # Ensure only one primary image per product
#             self.__class__.objects.filter(
#                 product=self.product,
#                 is_primary=True
#             ).update(is_primary=False)
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"Image for {self.product.name}"


# class ProductReview(BaseModel):
#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE,
#         related_name='reviews'
#     )
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='product_reviews'
#     )
#     rating = models.PositiveSmallIntegerField(
#         validators=[MinValueValidator(1), MaxValueValidator(5)]
#     )
#     comment = models.TextField(blank=True)
#     is_verified = models.BooleanField(default=False)

#     class Meta:
#         ordering = ['-created_at']
#         indexes = [
#             models.Index(fields=['product', 'rating']),
#             models.Index(fields=['user', 'product']),
#         ]
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['user', 'product'],
#                 name='unique_user_product_review'
#             )
#         ]

#     def clean(self):
#         if self.rating < 1 or self.rating > 5:
#             raise ValidationError("Rating must be between 1 and 5")

#     def save(self, *args, **kwargs):
#         self.full_clean()
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"Review for {self.product.name} by {self.user.username}"
