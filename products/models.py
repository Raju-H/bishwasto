# from django.db import models
# from django.conf import settings
# from django.core.cache import cache
# from django.core.validators import MinValueValidator, MaxValueValidator
# from django.core.exceptions import ValidationError
# from django.utils.text import slugify
# from accounts.models import BaseModel
# from shops.models import Shop
# from decimal import Decimal


# class CategoryQuerySet(models.QuerySet):
#     def active(self):
#         return self.filter(is_active=True)

#     def with_products_count(self):
#         return self.annotate(products_count=models.Count('products'))


# class ProductCategory(BaseModel):
#     shop = models.ForeignKey(
#         Shop, 
#         on_delete=models.CASCADE,
#         related_name='categories'
#     )
#     name = models.CharField(max_length=255, db_index=True)
#     slug = models.SlugField(max_length=255, unique=True)
#     description = models.TextField(blank=True)
#     is_active = models.BooleanField(default=True)

#     objects = CategoryQuerySet.as_manager()

#     class Meta:
#         verbose_name_plural = 'Product categories'
#         ordering = ['name']
#         indexes = [
#             models.Index(fields=['name', 'slug']),
#             models.Index(fields=['shop', 'is_active']),
#         ]

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.name)
#         self._invalidate_cache()
#         super().save(*args, **kwargs)

#     def _invalidate_cache(self):
#         cache_keys = [
#             f'category_{self.id}',
#             f'shop_categories_{self.shop_id}'
#         ]
#         cache.delete_many(cache_keys)

#     def __str__(self):
#         return f"{self.name} - {self.shop.name}"


# class ProductSubCategory(BaseModel):
#     category = models.ForeignKey(
#         ProductCategory, 
#         on_delete=models.CASCADE,
#         related_name='subcategories'
#     )
#     name = models.CharField(max_length=255, db_index=True)
#     slug = models.SlugField(max_length=255, unique=True)
#     description = models.TextField(blank=True)
#     is_active = models.BooleanField(default=True)

#     objects = CategoryQuerySet.as_manager()

#     class Meta:
#         verbose_name_plural = 'Product subcategories'
#         ordering = ['name']
#         indexes = [
#             models.Index(fields=['name', 'slug']),
#             models.Index(fields=['category', 'is_active']),
#         ]

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.name)
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.name} - {self.category.name}"


# class ProductQuerySet(models.QuerySet):
#     def active(self):
#         return self.filter(is_active=True)

#     def low_stock(self, threshold_percentage=20):
#         """
#         Returns products where stock is at or below threshold percentage above reorder level.
        
#         Example: If receivings_stock is 100 and threshold_percentage is 20,
#         products with stock_quantity <= 120 will be considered low stock.
#         """
#         return self.annotate(
#             threshold_qty=models.F('receivings_stock') * (1 + threshold_percentage/100)
#         ).filter(stock_quantity__lte=models.F('threshold_qty'))

#     def out_of_stock(self):
#         """Returns products with zero stock."""
#         return self.filter(stock_quantity=0)

#     def critical_stock(self):
#         """Returns products where stock is at or below reorder level."""
#         return self.filter(stock_quantity__lte=models.F('receivings_stock'))

#     def with_related(self):
#         return self.select_related(
#             'shop', 'category', 'sub_category'
#         ).prefetch_related('images', 'reviews')


# class Product(BaseModel):
#     shop = models.ForeignKey(
#         Shop, 
#         on_delete=models.CASCADE,
#         related_name='products'
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
#         related_name='products'
#     )
#     sub_category = models.ForeignKey(
#         ProductSubCategory,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='products'
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
#         validators=[MinValueValidator(Decimal('0.01'))]
#     )
#     wholesale_price = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         validators=[MinValueValidator(Decimal('0.01'))]
#     )
#     retail_price = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         validators=[MinValueValidator(Decimal('0.01'))]
#     )
#     stock_quantity = models.PositiveIntegerField(default=0)
#     receivings_stock = models.PositiveIntegerField(default=0)
#     order = models.PositiveIntegerField(default=0)
#     stock_warning_threshold = models.PositiveIntegerField(
#         default=10,
#         validators=[MinValueValidator(1), MaxValueValidator(100)],
#         help_text="Percentage of reorder level at which stock is considered low"
#     )
#     is_active = models.BooleanField(default=True)

#     objects = ProductQuerySet.as_manager()

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
