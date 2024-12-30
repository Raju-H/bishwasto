from django.urls import path

from .views import *
urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('create/', ProductCreateView.as_view(), name='product_create'),
    path('update/<uuid:pk>/', ProductUpdateView.as_view(), name='product_update'),
]


urlpatterns += [
    path('category/', ProductCategoryListView.as_view(), name='product_category_list'),
    path('category/create/', ProductCategoryCreateUpdateView.as_view(), name='product_category_create'),
    path('category/update/<uuid:pk>/', ProductCategoryCreateUpdateView.as_view(), name='product_category_update'),
]

urlpatterns += [
    path('category/sub/', ProductSubCategoryListView.as_view(), name='product_sub_category_list'),
    path('category/sub/create/', ProductSubCategoryCreateUpdateView.as_view(), name='product_sub_category_create'),
    path('category/sub/update/<uuid:pk>/', ProductSubCategoryCreateUpdateView.as_view(), name='product_sub_category_update'),
]

urlpatterns += [
    path('my/', ShopProductListView.as_view(), name='shop_product_list'),
    path('my/create/', ShopProductCreateView.as_view(), name='shop_product_create'),
    path('my/update/<uuid:pk>/', ShopProductUpdateView.as_view(), name='shop_product_update'),
]