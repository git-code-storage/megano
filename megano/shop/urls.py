from django.urls import path
from . import views

urlpatterns = [
    path('<slug:category_slug>/', views.ProductByCategoryListView.as_view(), name='product_by_category'),
    path('', views.index, name='index'),
]