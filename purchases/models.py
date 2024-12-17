# from django.db import models, transaction
# from django.core.cache import cache
# from django.core.validators import MinValueValidator
# from django.core.exceptions import ValidationError
# from django.utils import timezone
# from django.conf import settings
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from decimal import Decimal
# import logging

# from accounts.models import BaseModel
# from products.models import Product

# logger = logging.getLogger('inventory')




# class PurchaseOrderQuerySet(models.QuerySet):
#     def pending(self):
#         """Get pending purchase orders."""
#         return self.filter(is_received=False)
    
#     def received(self):
#         """Get received purchase orders."""
#         return self.filter(is_received=True)
    
#     def by_supplier(self, supplier_id):
#         """Get orders for a specific supplier."""
#         return self.filter(supplier_id=supplier_id)
    
#     def with_related(self):
#         """Get orders with related data preloaded."""
#         return self.select_related('product', 'supplier')


# class PurchaseOrder(BaseModel):
#     STATUS_CHOICES = (
#         ('pending', 'Pending'),
#         ('partial', 'Partially Received'),
#         ('completed', 'Completed'),
#         ('cancelled', 'Cancelled'),
#     )

#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE,
#         related_name='purchase_orders'
#     )
#     new_price = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         blank=True,
#         null=True,
#         validators=[MinValueValidator(Decimal('0.01'))],
#         help_text="New buying price for the product"
#     )
#     quantity_ordered = models.PositiveIntegerField(
#         validators=[MinValueValidator(1)],
#         help_text="Quantity ordered"
#     )
#     quantity_received = models.PositiveIntegerField(
#         default=0,
#         validators=[MinValueValidator(0)],
#         help_text="Quantity received"
#     )
#     supplier = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='supplied_orders'
#     )
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default='pending'
#     )
#     is_received = models.BooleanField(
#         default=False,
#         help_text="Whether the order has been received"
#     )
#     received_date = models.DateTimeField(
#         null=True,
#         blank=True
#     )
#     notes = models.TextField(
#         blank=True,
#         help_text="Additional notes about the purchase order"
#     )

#     objects = PurchaseOrderQuerySet.as_manager()

#     class Meta:
#         ordering = ['-created_at']
#         indexes = [
#             models.Index(fields=['product', 'supplier']),
#             models.Index(fields=['status', 'is_received']),
#             models.Index(fields=['created_at', 'received_date']),
#         ]
#         permissions = [
#             ("can_approve_orders", "Can approve purchase orders"),
#             ("can_receive_orders", "Can receive purchase orders"),
#         ]

#     def clean(self):
#         """Validate purchase order data."""
#         super().clean()
#         if self.quantity_received > self.quantity_ordered:
#             raise ValidationError("Received quantity cannot exceed ordered quantity")
#         if self.is_received and self.quantity_received == 0:
#             raise ValidationError("Cannot mark as received with zero quantity")
#         if self.new_price and self.new_price <= 0:
#             raise ValidationError("New price must be greater than zero")

#     def save(self, *args, **kwargs):
#         """Override save to handle status updates and validation."""
#         self.full_clean()
        
#         # Update status based on quantities
#         if self.quantity_received == 0:
#             self.status = 'pending'
#         elif self.quantity_received == self.quantity_ordered:
#             self.status = 'completed'
#         elif self.quantity_received < self.quantity_ordered:
#             self.status = 'partial'

#         # Set received date if marked as received
#         if self.is_received and not self.received_date:
#             self.received_date = timezone.now()

#         self._invalidate_cache()
#         super().save(*args, **kwargs)

#     def _invalidate_cache(self):
#         """Invalidate related caches."""
#         cache_keys = [
#             f'purchase_order_{self.pk}',
#             f'supplier_orders_{self.supplier_id}',
#             f'product_orders_{self.product_id}',
#             f'pending_orders_{self.product.shop_id}'
#         ]
#         cache.delete_many(cache_keys)

#     def receive_order(self, quantity: int, update_price: bool = False) -> None:
#         """
#         Process receiving of ordered items.
#         """
#         try:
#             with transaction.atomic():
#                 if quantity > (self.quantity_ordered - self.quantity_received):
#                     raise ValidationError("Receiving more than ordered quantity")

#                 previous_quantity = self.quantity_received
#                 self.quantity_received += quantity
#                 self.is_received = self.quantity_received == self.quantity_ordered
                
#                 # Update product price if specified
#                 if update_price and self.new_price:
#                     self.product.buying_price = self.new_price
#                     self.product.save(update_fields=['buying_price'])

#                 self.save()

#                 # Update product's receivings_stock
#                 self.product.receivings_stock += quantity
#                 self.product.stock_quantity += quantity
#                 self.product.save(update_fields=['receivings_stock', 'stock_quantity'])

#                 logger.info(
#                     f"Received {quantity} units for PO {self.pk}. "
#                     f"Product {self.product.pk} stock updated."
#                 )

#         except Exception as e:
#             logger.error(f"Error receiving order {self.pk}: {str(e)}")
#             raise

#     def cancel_order(self) -> None:
#         """
#         Cancel the purchase order.
#         """
#         if self.is_received:
#             raise ValidationError("Cannot cancel received order")
        
#         self.status = 'cancelled'
#         self.save(update_fields=['status'])

#     def get_order_details(self) -> dict:
#         """
#         Get cached order details.
#         """
#         cache_key = f'purchase_order_{self.pk}'
#         details = cache.get(cache_key)
        
#         if details is None:
#             details = {
#                 'id': self.pk,
#                 'product': self.product.name,
#                 'supplier': self.supplier.get_full_name(),
#                 'quantity_ordered': self.quantity_ordered,
#                 'quantity_received': self.quantity_received,
#                 'remaining_quantity': self.quantity_ordered - self.quantity_received,
#                 'status': self.status,
#                 'total_cost': self.new_price * self.quantity_ordered if self.new_price else None,
#                 'created_at': self.created_at,
#                 'received_date': self.received_date
#             }
#             cache.set(cache_key, details, timeout=settings.CACHE_TTL_MEDIUM)
        
#         return details

#     def __str__(self):
#         return f"PO-{self.pk}: {self.product.name} ({self.quantity_ordered} units)"


# @receiver(post_save, sender=PurchaseOrder)
# def update_product_stock(sender, instance: PurchaseOrder, created: bool, **kwargs):
#     """
#     Update product's receivings_stock when purchase order is received.
#     """
#     if not created and instance.is_received:
#         try:
#             with transaction.atomic():
#                 product = instance.product
                
#                 # Get previous state
#                 previous = PurchaseOrder.objects.filter(
#                     pk=instance.pk
#                 ).only('quantity_received').first()
                
#                 quantity_change = (
#                     instance.quantity_received -
#                     (previous.quantity_received if previous else 0)
#                 )

#                 if quantity_change > 0:
#                     # Update product stock
#                     Product.objects.filter(pk=product.pk).update(
#                         receivings_stock=models.F('receivings_stock') + quantity_change,
#                         stock_quantity=models.F('stock_quantity') + quantity_change
#                     )

#                     logger.info(
#                         f"Updated product {product.pk} stock: "
#                         f"Added {quantity_change} units from PO {instance.pk}"
#                     )

#         except Exception as e:
#             logger.error(f"Error updating product stock: {str(e)}")
#             raise
