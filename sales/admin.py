from django.contrib import admin
from .models import Sales, SalesItems

class SalesItemsInline(admin.TabularInline):
    model = SalesItems
    extra = 1
    fields = ['product', 'sale_price', 'profit_in_percentage', 'discount_in_percentage', 'quantity']


@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer', 'employee', 'payment_method', 'notes']
    search_fields = ['invoice_number', 'customer__username']
    inlines = [SalesItemsInline]
