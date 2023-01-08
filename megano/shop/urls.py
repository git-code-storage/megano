from django.urls import path
from . import views

urlpatterns = [
    path('testform/', views.testform, name='testform'),
    path('cart/add/<slug:product_slug>/', views.add_cart, name='cart_add'),
    path('product/<slug:product_slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('category/<slug:category_slug>/<str:sort>/', views.products_by_category,
         name='products_by_category'),
    path('', views.index, name='index'),
]