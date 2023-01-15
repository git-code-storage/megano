from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('account/', views.account, name='account'),
    path('history_order/', views.history_order, name='history_order'),
    path('registration/', views.registration, name='registration'),
]