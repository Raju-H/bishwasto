from django.db import models
from accounts.models import BaseModel
from django.conf import settings


# Tax model
class Tax(BaseModel):
    name = models.CharField(max_length=255, db_index=True)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_taxes'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Taxes'

    def __str__(self):
        return f"{self.name} - {self.rate}%"