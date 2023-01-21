from django.urls import path
from . import views

urlpatterns = [
    path('order/one/', views.order_step_one, name='order_step_one'),
    path('order/two/', views.order_step_two, name='order_step_two'),
    path('order/three/', views.order_step_three, name='order_step_three'),
    path('order/four/', views.order_step_four, name='order_step_four'),
    path('order/<int:pk>/', views.oneorder, name='oneorder'),
    path('payment/', views.payment, name='payment'),
    path('search_results/', views.SearchResultsView.as_view(), name='search_results'),
    path('paymentprocedure/', views.payment_procedure, name='payment_procedure'),
    path('cart/', views.cart, name='cart'),
    path('cart/remove_product/<slug:product_slug>/', views.remove_product_cart, name='cart_remove_product'),
    path('cart/remove/<slug:product_slug>/', views.remove_cart, name='cart_remove'),
    path('cart/cook_add/<slug:product_slug>/', views.add_cart_from_cookies, name='cook_add'),
    path('cart/add/<slug:product_slug>/<int:amt>/', views.add_cart, name='cart_add'),
    path('product/<slug:product_slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('category/<slug:category_slug>/<str:sort>/', views.products_by_category,
         name='products_by_category'),
    path('about/', views.about, name='about'),
    path('blog/', views.blog, name='blog'),
    path('', views.index, name='index'),
]