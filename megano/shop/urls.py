from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart, name='cart'),
    path('cart/remove_product/<slug:product_slug>/', views.remove_product_cart, name='cart_remove_product'),
    path('cart/remove/<slug:product_slug>/', views.remove_cart, name='cart_remove'),
    path('cart/add/<slug:product_slug>/<int:amt>/', views.add_cart, name='cart_add'),
    path('product/<slug:product_slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('category/<slug:category_slug>/<str:sort>/', views.products_by_category,
         name='products_by_category'),
    path('', views.index, name='index'),
]