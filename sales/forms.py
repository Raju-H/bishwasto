from django import forms
from .models import Sales, SalesItems

class SalesForm(forms.ModelForm):
    class Meta:
        model = Sales
        fields = ['customer', 'employee', 'payment_method', 'notes']

class SalesItemsForm(forms.ModelForm):
    class Meta:
        model = SalesItems
        fields = ['product', 'quantity', 'discount_in_percentage']
