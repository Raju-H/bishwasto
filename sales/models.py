from django.db import models, transaction
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from accounts.models import BaseModel
from django.utils.crypto import get_random_string
from products.models import ShopProduct


"""
# Product models fields
fields = ['category', 'sub_category', 'name', 'description', 'model', 'sku', 'isbn', 'variant', 'is_expirable', 'expiry_date', 'weight_unit', 'weight', 'length_unit', 'length', 'width', 'height', 'avatar', 'is_active']

# ShopProduct models fields
fields = [
        'shop', 'supplier', 'product', 'buying_price', 'wholesale_price', 'retail_price', 'qrcode',
        'stock_quantity', 'receivings_stock', 'sort_order',
        'stock_warning_threshold', 'default_tax_rate', 'is_active'

# Sales models fields
fields = ['customer', 'payment_method', 'sub_total', 'grand_total', 'amount_payed', 'amount_change', 'notes']

# SalesItems Models fields
fields = ['product', 'sale_price', 'profit_in_percentage', 'discount_in_percentage', 'quantity']

"""



class Sales(BaseModel):
    PAYMENT_CHOICES = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('MOBILE', 'Mobile Payment'),
        ('BANK', 'Bank Transfer'),
        ('DUE', 'Due Payment'),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='sales_customer',
        null=True,
        blank=True
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='sales_employee'
    )
    invoice_number = models.CharField(
        max_length=255, 
        unique=True, 
        db_index=True
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_CHOICES,
        default='CASH'
    )
    sub_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=0
    )
    grand_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=0
    )
    amount_payed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=0
    )
    amount_change = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=0
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Sale'
        verbose_name_plural = 'Sales'

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.customer.username}"
    
    def sum_items(self):
        salesitems = SalesItems.objects.filter(sales=self.id)
        return sum(items.quantity for items in salesitems)

    def save(self, *args, **kwargs):
        # Generate invoice number if not provided
        if not self.invoice_number:
            self.invoice_number = self._generate_invoice_number()
        
        # Perform validations
        self.full_clean()
        
        super().save(*args, **kwargs)

    def _generate_invoice_number(self):
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        random_string = get_random_string(length=4).upper()
        return f"INV-{random_string}-{timestamp}"







class SalesItems(BaseModel):
    sales = models.ForeignKey(
        Sales,
        on_delete=models.CASCADE,
        related_name='sales_items'
    )
    product = models.ForeignKey(
        ShopProduct, 
        on_delete=models.CASCADE,
        related_name='salesitem_products'
    )
    sale_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=0
    )
    profit_in_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )
    discount_in_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Sale Item'
        verbose_name_plural = 'Sale Items'
        
    def __str__(self):
        return f"Sale Item for {self.product.name} - {self.quantity}"
    
    def clean(self):
        if self.quantity > self.product.stock_quantity:
            raise ValidationError("Insufficient stock quantity")

    def save(self, *args, **kwargs):
        # Perform validations
        self.full_clean()
        super().save(*args, **kwargs)


@receiver(post_save, sender=SalesItems)
def update_product_stock_on_create_or_update(sender, instance, created, **kwargs):
    """Update product stock quantity when a SalesItem is created or updated."""
    with transaction.atomic():
        product = instance.product
        if created:
            # Decrease stock quantity when a new sale item is created
            product.stock_quantity -= instance.quantity
        else:
            # If updating, adjust based on the new quantity vs old quantity.
            old_quantity = SalesItems.objects.get(pk=instance.pk).quantity
            product.stock_quantity += old_quantity  # Restore old quantity
            product.stock_quantity -= instance.quantity  # Deduct new quantity

        product.save()