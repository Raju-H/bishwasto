from django.urls import path
from .views import *

urlpatterns = [
    path('create/', SubscriptionPlanCreateUpdateView.as_view(), name='subscription_create'),
    path('update/<uuid:pk>/', SubscriptionPlanCreateUpdateView.as_view(), name='subscription_update'),
    path('', SubscriptionPlanListView.as_view(), name='subscription_list'),
]
