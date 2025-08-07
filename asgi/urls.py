from django.urls import path
from . import views


urlpatterns = [
    path('home_asgi/', views.home_asgi, name='home_asgi'),
    path('register_asgi/', views.register_view, name='register_asgi'),
    path('login_asgi/', views.LoginView.as_view(), name='login_asgi'),
    path('logout_asgi/', views.logout_asgi, name='logout_asgi'),
]
