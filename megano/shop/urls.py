from django.urls import path
from . import views

urlpatterns = [
    path('cart/add/<slug:product_slug>/', views.add_cart, name='cart_add'),
    path('product/<slug:product_slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('<slug:category_slug>/', views.ProductByCategoryListView.as_view(), name='products_by_category'),
    path('', views.index, name='index'),
]