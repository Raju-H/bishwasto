from django.urls import path
from .views import *

urlpatterns = [
    path('', ShopListView.as_view(), name='shop_list'),
    path('create/', ShopCreateView.as_view(), name='shop_create'),
    path('update/<uuid:pk>/', ShopUpdateView.as_view(), name='shop_update'),
    path('my/', MyShopsListView.as_view(), name='myshop_list'),
]
