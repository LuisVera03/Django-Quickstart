from django.urls import path
from . import views

app_name = 'json_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.user_register, name='user_register'),
    path('login/', views.user_login, name='user_login'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.user_logout, name='user_logout'),
]
