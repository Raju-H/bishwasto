from django.db import models
from django.conf import settings
from django.core.cache import cache
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from accounts.models import BaseModel


class ShopQuerySet(models.QuerySet):
    def active(self):
        """Return only active shops with valid subscriptions."""
        return self.filter(subscription_plan__isnull=False)

    def with_related(self):
        """Load all related data efficiently."""
        return (self
                .select_related('subscription_plan')
                .prefetch_related('owner', 'employees'))

    def by_owner(self, user_id):
        """Get shops for a specific owner."""
        cache_key = f'owner_shops_{user_id}'
        shops = cache.get(cache_key)
        
        if shops is None:
            shops = list(self.filter(owner=user_id))
            cache.set(cache_key, shops, timeout=settings.CACHE_TTL_MEDIUM)
        
        return shops


class ShopManager(models.Manager):
    def get_queryset(self):
        return ShopQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def with_related(self):
        return self.get_queryset().with_related()


class Shop(BaseModel):
    PHONE_REGEX = r'^\+?1?\d{9,15}$'
    PHONE_MESSAGE = "Phone number must be entered in the format: '+8801234567890'. Up to 15 digits allowed."

    owner = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='owned_shops',
        verbose_name='Shop Owners'
    )
    
    subscription_plan = models.ForeignKey(
        "subscriptions.ShopSubscriptionPlan",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shops'
    )
    
    name = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Shop name"
    )
    
    address = models.CharField(
        max_length=255,
        help_text="Physical address of the shop"
    )
    
    phone_number = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=PHONE_REGEX,
                message=PHONE_MESSAGE
            )
        ],
        help_text="Contact phone number"
    )
    
    employees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='employed_at',
        blank=True,
        verbose_name='Shop Employees'
    )

    objects = ShopManager()

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['name', 'address']),
        ]
        ordering = ['name']
        verbose_name = 'Shop'
        verbose_name_plural = 'Shops'
        permissions = [
            ("manage_shop", "Can manage shop settings"),
            ("view_analytics", "Can view shop analytics"),
        ]

    def __str__(self):
        return f"{self.name} ({self.address})"

    def clean(self):
        """Validate shop data."""
        super().clean()
        if not self.name:
            raise ValidationError("Shop name is required")
        if not self.address:
            raise ValidationError("Shop address is required")

    def save(self, *args, **kwargs):
        """Override save to handle cache invalidation."""
        self.full_clean()
        self._invalidate_caches()
        super().save(*args, **kwargs)

    def _invalidate_caches(self):
        """Invalidate related caches."""
        cache_keys = [
            f'shop_employees_{self.id}',
            f'shop_details_{self.id}',
            *[f'owner_shops_{owner.id}' for owner in self.owner.all()]
        ]
        cache.delete_many(cache_keys)

    def get_employees(self):
        """Get cached list of employees."""
        cache_key = f'shop_employees_{self.id}'
        employees = cache.get(cache_key)
        
        if employees is None:
            employees = list(
                self.employees
                .select_related('user')
                .only('id', 'username', 'email', 'first_name', 'last_name')
            )
            cache.set(cache_key, employees, timeout=settings.CACHE_TTL_MEDIUM)
        
        return employees

    def add_employee(self, user):
        """Add an employee to the shop."""
        if user not in self.employees.all():
            self.employees.add(user)
            self._invalidate_caches()

    def remove_employee(self, user):
        """Remove an employee from the shop."""
        if user in self.employees.all():
            self.employees.remove(user)
            self._invalidate_caches()

    def is_owner(self, user):
        """Check if user is an owner."""
        return self.owner.filter(id=user.id).exists()

    def is_employee(self, user):
        """Check if user is an employee."""
        return self.employees.filter(id=user.id).exists()

    @property
    def is_active(self):
        """Check if shop has active subscription."""
        return bool(self.subscription_plan)

    def get_details(self):
        """Get cached shop details."""
        cache_key = f'shop_details_{self.id}'
        details = cache.get(cache_key)
        
        if details is None:
            details = {
                'id': self.id,
                'name': self.name,
                'address': self.address,
                'phone': self.phone_number,
                'employee_count': self.employees.count(),
                'owner_count': self.owner.count(),
                'has_subscription': self.is_active
            }
            cache.set(cache_key, details, timeout=settings.CACHE_TTL_MEDIUM)
        
        return details
