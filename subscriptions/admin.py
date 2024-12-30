from django.contrib import admin
from .models import *




class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration_months', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'duration_months']
    list_editable = ['price', 'duration_months', 'is_active']
    list_per_page = 10

admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)