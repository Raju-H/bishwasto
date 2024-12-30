from django import forms
from .models import *

class SalesForm(forms.ModelForm):
    class Meta:
        model = Sales
        fields = ['customer', 'payment_method', 'sub_total', 'grand_total', 'amount_payed', 'amount_change', 'notes']


class SalesItemsForm(forms.ModelForm):
    class Meta:
        model = SalesItems
        fields = ['product', 'sale_price', 'profit_in_percentage', 'discount_in_percentage', 'quantity']
