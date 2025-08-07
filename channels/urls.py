from django.urls import path
from . import views


urlpatterns = [
    path('home_channels/', views.home_channels, name='home_channels'),
    path('register_channels/', views.register_view, name='register_channels'),
    path('login_channels/', views.LoginView.as_view(), name='login_channels'),
    path('logout_channels/', views.logout_channels, name='logout_channels'),
]
