from django.contrib import admin
from .models import *

class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'email', 'website')
    search_fields = ('name', 'phone_number', 'email', 'website')
    list_filter = ('name', 'phone_number', 'email', 'website')
    list_editable = ('phone_number', 'email', 'website')


admin.site.register(Shop, ShopAdmin)