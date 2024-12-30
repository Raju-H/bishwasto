from django.urls import path
from .views import *
urlpatterns = [
    path('', SalesListView.as_view(), name='sales_list'),
    path('create/', sales_create_view, name='sales_create'),
]


urlpatterns += [
    path('get_shops_product/', get_shops_product_ajax_view, name='get_shops_product'),
]