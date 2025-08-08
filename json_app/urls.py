from django.urls import path
from . import views


urlpatterns = [
    path('home_json', views.home, name='home_json'),
    path('register_json/', views.user_register, name='register_json'),
    path('login_json/', views.user_login, name='login_json'),
    path('logout_json/', views.user_logout, name='logout_json'),
    path('profile_json/', views.profile, name='profile_json'),

    # CRUD endpoints for JSON fetch
    path('table1/', views.table1_crud, name='table1_crud'),
    path('table2/', views.table2_crud, name='table2_crud'),
    path('table3/', views.table3_crud, name='table3_crud'),
    
    # Table1 search
    path('search_json/', views.search_view, name='search_json'),
    path('search_all_json/', views.search_all_data, name='search_all_json'),
]
