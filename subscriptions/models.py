from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from accounts.models import BaseModel
from decimal import Decimal




class SubscriptionPlan(BaseModel):

    name = models.CharField(
        max_length=100, 
        db_index=True,
        help_text="Name of the subscription plan"
    )

    description = models.TextField(
        blank=True,
        help_text="Detailed description of the subscription plan"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        db_index=True,
        help_text="Monthly price of the subscription plan"
    )

    duration_months = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(60)
        ],
        help_text=(
            "Duration of subscription plan in months & Max value is 60 months (5 years)"
        )
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='subscriptionplan_created_by',
        null=True
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the subscription plan is currently active"
    )

    class Meta:
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'

    def __str__(self) -> str:
        return f"{self.name} - {self.duration_months} - {self.price}"





# class ShopSubscriptionPlan(BaseModel):
#     shop = models.ForeignKey(
#         Shop,
#         on_delete=models.CASCADE,
#         related_name='subscriptions'
#     )
#     subscription = models.ForeignKey(
#         Subscription,
#         on_delete=models.CASCADE,
#         related_name='shop_subscriptions'
#     )
#     start_date = models.DateField()
#     end_date = models.DateField()
#     creatd_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         related_name='shop_subscriptionsplan_created',
#         null=True
#     )

#     objects = models.Manager()
#     active = ActiveSubscriptionManager()

#     class Meta:
#         indexes = [
#             models.Index(fields=['start_date', 'end_date']),
#             models.Index(fields=['shop', 'subscription']),
#         ]
#         constraints = [
#             models.CheckConstraint(
#                 check=models.Q(end_date__gt=models.F('start_date')),
#                 name='valid_date_range'
#             )
#         ]

#     def __str__(self):
#         return f"{self.shop.name} - {self.subscription.name}"

#     def save(self, *args, **kwargs):
#         with transaction.atomic():
#             # Validate dates
#             self.active.validate_dates(self.start_date, self.end_date)
            
#             # Check overlapping only for new subscriptions
#             if not self.pk and self.active.check_overlapping(
#                 self.shop_id, self.start_date, self.end_date
#             ):
#                 raise ValueError("Subscription period overlaps with existing subscription")

#             # Invalidate related caches
#             self._invalidate_caches()
            
#             super().save(*args, **kwargs)

#     def _invalidate_caches(self):
#         """Invalidate related caches."""
#         cache_keys = [
#             f'sub_status_{self.pk}',
#             f'shop_subs_{self.shop_id}',
#             f'active_subs_{self.shop_id}'
#         ]
#         cache.delete_many(cache_keys)

#     @property
#     def is_active(self):
#         """Check if subscription is active with caching."""
#         cache_key = f'sub_status_{self.pk}'
#         status = cache.get(cache_key)
        
#         if status is None:
#             today = timezone.now().date()
#             if self.start_date <= today <= self.end_date:
#                 status = 'active'
#             elif today < self.start_date:
#                 status = 'pending'
#             else:
#                 status = 'expired'
                
#             cache.set(cache_key, status, timeout=settings.CACHE_TTL_LONG)
            
#             if self.subscription.status != status:
#                 self.subscription.status = status
#                 self.subscription.save(update_fields=['status'])
                
#         return status == 'active'

#     @classmethod
#     def get_active_subscriptions(cls, shop_id):
#         """Get active subscriptions for a shop with caching."""
#         cache_key = f'active_subs_{shop_id}'
#         subs = cache.get(cache_key)
        
#         if subs is None:
#             today = timezone.now().date()
#             subs = list(cls.objects
#                        .filter(
#                            shop_id=shop_id,
#                            start_date__lte=today,
#                            end_date__gte=today
#                        )
#                        .select_related('subscription')
#                        .only('id', 'start_date', 'end_date',
#                              'subscription__name', 'subscription__price'))
#             cache.set(cache_key, subs, timeout=settings.CACHE_TTL_LONG)
            
#         return subs
