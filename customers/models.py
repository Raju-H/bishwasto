from django.db import models
from django.conf import settings
from accounts.models import BaseModel


class Customer(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer'
    )
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.user.email}"
    
    def get_ful_name(self):
        return f"{self.user.first_name} {self.user.last_name}"
    

    def to_select2(self):
        item = {
            'label': self.get_ful_name(),
            'value': self.id
        }
        return item