from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.user_register, name='user_register'),
    path('login/', views.user_login, name='user_login'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.user_logout, name='user_logout'),

    # CRUD endpoints for JSON fetch
    path('table1/', views.table1_crud, name='table1_crud'),
    path('table2/', views.table2_crud, name='table2_crud'),
    path('table3/', views.table3_crud, name='table3_crud'),
]
