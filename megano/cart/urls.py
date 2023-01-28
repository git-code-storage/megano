from django.urls import path
from . import views

urlpatterns = [
    path('order/one/', views.order_step_one, name='order_step_one'),
    path('order/two/', views.order_step_two, name='order_step_two'),
    path('order/three/', views.order_step_three, name='order_step_three'),
    path('order/four/', views.order_step_four, name='order_step_four'),
    path('order/<int:pk>/', views.oneorder, name='oneorder'),
    path('payment/', views.payment, name='payment'),
    path('paymentprocedure/', views.payment_procedure, name='payment_procedure'),
]