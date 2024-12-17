from django.db import models, transaction
from django.core.cache import cache
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from functools import lru_cache
from accounts.models import BaseModel
# from shops.models import Shop
from django.core.exceptions import ValidationError



class ActiveSubscriptionManager(models.Manager):
    def get_queryset(self):
        """Return only active subscriptions with optimized query."""
        today = timezone.now().date()
        return (super()
               .get_queryset()
               .filter(start_date__lte=today, end_date__gte=today)
               .select_related('shop', 'subscription')
               .only('id', 'start_date', 'end_date', 
                    'shop__name', 'subscription__name'))

    def validate_dates(self, start_date, end_date):
        """Validate subscription dates."""
        if not isinstance(start_date, (timezone.datetime, timezone.datetime.date)):
            raise ValueError("Invalid start date format")
        if not isinstance(end_date, (timezone.datetime, timezone.datetime.date)):
            raise ValueError("Invalid end date format")
        if end_date <= start_date:
            raise ValueError("End date must be after start date")

    def check_overlapping(self, shop_id, start_date, end_date):
        """Check for overlapping subscriptions with caching."""
        cache_key = f'overlap_sub_{shop_id}_{start_date}_{end_date}'
        result = cache.get(cache_key)
        
        if result is None:
            result = self.filter(
                shop_id=shop_id,
                start_date__lt=end_date,
                end_date__gt=start_date
            ).exists()
            cache.set(cache_key, timeout=settings.CACHE_TTL_MEDIUM)
        return result


class Subscription(BaseModel):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'), 
        ('expired', 'Expired'),
        ('failed', 'Failed'),
    )

    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        db_index=True
    )
    duration_months = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(60)
        ]
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )

    objects = models.Manager()
    active = ActiveSubscriptionManager()

    class Meta:
        indexes = [
            models.Index(fields=['price', 'status']),
            models.Index(fields=['status', 'duration_months']),
        ]
        ordering = ['price']

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    @lru_cache(maxsize=128)
    def get_total_price(self):
        """Calculate total price with caching."""
        return self.price * self.duration_months

    def clean(self):
        super().clean()
        if self.price < 0:
            raise ValidationError("Price cannot be negative")


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
