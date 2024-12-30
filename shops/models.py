from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from accounts.models import BaseModel
from PIL import Image


class Shop(BaseModel):

    LOGO_MAX_SIZE = (300, 300)

    PHONE_REGEX = r'^\+?1?\d{9,15}$'
    PHONE_MESSAGE = "Phone number must be entered in the format: '+8801234567890'. Up to 15 digits allowed."

    owner = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='owned_shops',
        verbose_name='Shop Owners'
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

    email = models.EmailField(
        max_length=255,
        help_text="Contact email address"
    )

    return_policy = models.TextField(
        help_text="Shop's return policy"
    )

    website = models.URLField(
        blank=True, null=True,
        help_text="Shop's website URL"
    )

    shop_logo = models.ImageField(
        upload_to='shops/logos/',
        blank=True,
        null=True,
        help_text=(
            "Recommended size: 300x300 pixels. Maximum file size: 1MB. "
            "Images will be automatically resized if larger. "
            "Supported formats: JPG, JPEG, PNG"
        )
    )

    employees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='employed_at',
        blank=True,
        verbose_name='Shop Employees'
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether the shop is currently active"
    )
    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['name', 'address']),
        ]
        verbose_name = 'Shop'
        verbose_name_plural = 'Shops'

    def __str__(self):
        return f"{self.name}"


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.shop_logo:
            img = Image.open(self.shop_logo.path)
            img.resize(self.LOGO_MAX_SIZE, Image.LANCZOS)
            # Save the optimized image back to the same file
            img.save(self.shop_logo.path)
            
        