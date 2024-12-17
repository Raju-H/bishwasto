# from decimal import Decimal
# from django.db import models, transaction
# from django.core.cache import cache
# from django.core.validators import MinValueValidator, MaxValueValidator
# from django.core.exceptions import ValidationError
# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
# from django.db.models import F, Sum
# from accounts.models import BaseModel
# from django.conf import settings
# from django.utils import timezone
# import logging


# logger = logging.getLogger(__name__)



# class SalesQuerySet(models.QuerySet):
#     def for_shop(self, shop_id):
#         return self.filter(shop_id=shop_id)
    
#     def for_period(self, start_date, end_date):
#         return self.filter(created_at__range=(start_date, end_date))
    
#     def with_related(self):
#         return self.select_related(
#             'customer', 
#             'shop', 
#             'product', 
#             'employee'
#         )
    
#     def total_sales(self):
#         return self.aggregate(
#             total=Sum(F('new_price') * F('quantity'))
#         )['total'] or Decimal('0.00')

# class Sales(BaseModel):
#     PAYMENT_CHOICES = [
#         ('CASH', 'Cash'),
#         ('CARD', 'Card'),
#         ('MOBILE', 'Mobile Payment'),
#     ]

#     STATUS_CHOICES = [
#         ('PENDING', 'Pending'),
#         ('COMPLETED', 'Completed'),
#         ('CANCELLED', 'Cancelled'),
#         ('REFUNDED', 'Refunded'),
#     ]

#     customer = models.ForeignKey(
#         settings.AUTH_USER_MODEL, 
#         on_delete=models.CASCADE, 
#         related_name='sales_customer'
#     )
#     shop = models.ForeignKey(
#         'shops.Shop', 
#         on_delete=models.CASCADE,
#         related_name='sales'
#     )
#     product = models.ForeignKey(
#         'products.Product', 
#         on_delete=models.CASCADE,
#         related_name='sales'
#     )
#     employee = models.ForeignKey(
#         settings.AUTH_USER_MODEL, 
#         on_delete=models.SET_NULL, 
#         null=True, 
#         blank=True, 
#         related_name='sales_employee'
#     )
#     invoice_number = models.CharField(
#         max_length=255, 
#         unique=True, 
#         db_index=True
#     )
#     new_price = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2,
#         validators=[MinValueValidator(Decimal('0.01'))]
#     )
#     original_price = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2,
#         validators=[MinValueValidator(Decimal('0.01'))]
#     )
#     profit_in_percentage = models.DecimalField(
#         max_digits=5, 
#         decimal_places=2,
#         validators=[MinValueValidator(0), MaxValueValidator(100)]
#     )
#     discount_percent = models.DecimalField(
#         max_digits=5, 
#         decimal_places=2,
#         default=0,
#         validators=[MinValueValidator(0), MaxValueValidator(100)]
#     )
#     quantity = models.PositiveIntegerField(
#         default=1,
#         validators=[MinValueValidator(1)]
#     )
#     payment_method = models.CharField(
#         max_length=10,
#         choices=PAYMENT_CHOICES,
#         default='CASH'
#     )
#     status = models.CharField(
#         max_length=10,
#         choices=STATUS_CHOICES,
#         default='PENDING'
#     )
#     sale_date = models.DateTimeField(default=timezone.now)
#     notes = models.TextField(blank=True)

#     objects = SalesQuerySet.as_manager()

#     class Meta:
#         verbose_name = 'Sale'
#         verbose_name_plural = 'Sales'
#         ordering = ['-sale_date']
#         indexes = [
#             models.Index(fields=['invoice_number']),
#             models.Index(fields=['sale_date', 'shop']),
#             models.Index(fields=['customer', 'status']),
#         ]

#     def __str__(self):
#         return f"Invoice #{self.invoice_number} - {self.customer.username}"

#     def clean(self):
#         from django.core.exceptions import ValidationError
#         if self.new_price > self.original_price:
#             raise ValidationError("New price cannot be greater than original price")
#         if self.quantity > self.product.stock_quantity:
#             raise ValidationError("Insufficient stock quantity")

#     def calculate_total(self):
#         return self.new_price * self.quantity

#     def calculate_discount_amount(self):
#         return (self.original_price * self.quantity) * (self.discount_percent / 100)

#     def calculate_profit(self):
#         total_cost = self.product.buying_price * self.quantity
#         total_revenue = self.new_price * self.quantity
#         return total_revenue - total_cost

#     def save(self, *args, **kwargs):
#         # Generate invoice number if not provided
#         if not self.invoice_number:
#             self.invoice_number = self._generate_invoice_number()
        
#         # Perform validations
#         self.full_clean()
        
#         # Update product stock
#         if self._state.adding:  # Only on creation
#             self.product.stock_quantity = F('stock_quantity') - self.quantity
#             self.product.save()

#         # Invalidate relevant caches
#         self._invalidate_cache()
        
#         super().save(*args, **kwargs)

#     def _generate_invoice_number(self):
#         from django.utils import timezone
#         timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
#         return f"INV-{self.shop.id}-{timestamp}"

#     def _invalidate_cache(self):
#         cache_keys = [
#             f'sale_{self.id}',
#             f'customer_sales_{self.customer_id}',
#             f'shop_sales_{self.shop_id}',
#             f'product_sales_{self.product_id}',
#         ]
#         cache.delete_many(cache_keys)




# @receiver(post_save, sender=Sales)
# def update_stock_on_sale(sender, instance, created, **kwargs):
#     """
#     Update product stock quantity when a sale is created or updated
#     """
#     try:
#         with transaction.atomic():
#             if created:
#                 # Check if enough stock is available
#                 if instance.product.stock_quantity < instance.quantity:
#                     raise ValidationError(
#                         f"Insufficient stock for product {instance.product.name}. "
#                         f"Available: {instance.product.stock_quantity}, Requested: {instance.quantity}"
#                     )
                
#                 instance.product.stock_quantity = F('stock_quantity') - instance.quantity
#                 instance.product.save()
                
#                 # Log the transaction
#                 logger.info(
#                     f"Stock reduced by {instance.quantity} units for product {instance.product.id} "
#                     f"due to sale {instance.invoice_number}"
#                 )
#             else:
#                 try:
#                     old_instance = Sales.objects.get(id=instance.id)
#                     if old_instance.quantity != instance.quantity:
#                         quantity_difference = old_instance.quantity - instance.quantity
                        
#                         # Check if enough stock is available for increase
#                         if quantity_difference < 0 and instance.product.stock_quantity < abs(quantity_difference):
#                             raise ValidationError(
#                                 f"Insufficient stock for product {instance.product.name} "
#                                 f"to update sale quantity"
#                             )
                        
#                         instance.product.stock_quantity = F('stock_quantity') + quantity_difference
#                         instance.product.save()
                        
#                         logger.info(
#                             f"Stock adjusted by {quantity_difference} units for product {instance.product.id} "
#                             f"due to sale update {instance.invoice_number}"
#                         )
#                 except Sales.DoesNotExist:
#                     logger.warning(f"Could not find original sale instance for {instance.id}")

#     except Exception as e:
#         logger.error(f"Error updating stock for sale {instance.invoice_number}: {str(e)}")
#         raise

# @receiver(post_delete, sender=Sales)
# def restore_stock_on_delete(sender, instance, **kwargs):
#     """
#     Restore product stock quantity when a sale is deleted
#     """
#     try:
#         with transaction.atomic():
#             instance.product.stock_quantity = F('stock_quantity') + instance.quantity
#             instance.product.save()
            
#             logger.info(
#                 f"Stock restored by {instance.quantity} units for product {instance.product.id} "
#                 f"due to sale deletion {instance.invoice_number}"
#             )
#     except Exception as e:
#         logger.error(f"Error restoring stock for deleted sale {instance.invoice_number}: {str(e)}")
#         raise
