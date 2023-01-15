from django.urls import path
from . import views

urlpatterns = [
    path('order/1/', views.order_step_one, name='order_step_one'),
    path('order/2/', views.order_step_two, name='order_step_two'),
    path('order/3/', views.order_step_three, name='order_step_three'),
    path('order/4/', views.order_step_four, name='order_step_four'),
    path('payment/', views.payment, name='payment'),
    path('paymentprocedure/', views.payment_procedure, name='payment_procedure'),
    path('cart/', views.cart, name='cart'),
    path('cart/remove_product/<slug:product_slug>/', views.remove_product_cart, name='cart_remove_product'),
    path('cart/remove/<slug:product_slug>/', views.remove_cart, name='cart_remove'),
    path('cart/cook_add/<slug:product_slug>/', views.add_cart_from_cookies, name='cook_add'),
    path('cart/add/<slug:product_slug>/<int:amt>/', views.add_cart, name='cart_add'),
    path('product/<slug:product_slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('category/<slug:category_slug>/<str:sort>/', views.products_by_category,
         name='products_by_category'),
    path('', views.index, name='index'),
]