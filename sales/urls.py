from django.urls import path
from .views import *
urlpatterns = [
    path('', SalesListView.as_view(), name='sales_list'),
    path('create/', SaleCreateView.as_view(), name='sales_create'),
    # path('search/', search_products, name='search_products'),
]


urlpatterns += [
    path('get_shops_product/', get_shops_product_ajax_view, name='get_shops_product'),
]