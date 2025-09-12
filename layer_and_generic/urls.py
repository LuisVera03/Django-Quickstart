from django.urls import path

from .views import (
    LoginView, RegisterView, LogoutView, home,
    # Table1 views
    Table1ListView, Table1DetailView, Table1CreateView, Table1UpdateView, Table1DeleteView,
    # Table2 views
    Table2ListView, Table2DetailView, Table2CreateView, Table2UpdateView, Table2DeleteView,
    # Table3 views
    Table3ListView, Table3DetailView, Table3CreateView, Table3UpdateView, Table3DeleteView,
    # API views
    Table1APIView, Table2APIView, Table3APIView, GenericTable1APIView,
)

urlpatterns = [
    # Authentication URLs
    path('home_layer_and_generic', home, name='home_layer_and_generic'),
    path('register_layer_and_generic/', RegisterView.as_view(), name='register_layer_and_generic'),
    path('login_layer_and_generic/', LoginView.as_view(), name='login_layer_and_generic'),
    path('logout_layer_and_generic/', LogoutView.as_view(), name='logout_layer_and_generic'),
    
    # Table1 CRUD (Legacy URLs for backward compatibility)
    path('ListView/', Table1ListView.as_view(), name='list'),
    path('<int:pk>/', Table1DetailView.as_view(), name='detail'),
    path('create/', Table1CreateView.as_view(), name='create'),
    path('<int:pk>/update/', Table1UpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', Table1DeleteView.as_view(), name='delete'),
    
    # Table1 CRUD (Standard URLs)
    path('table1/', Table1ListView.as_view(), name='table1_list'),
    path('table1/<int:pk>/', Table1DetailView.as_view(), name='table1_detail'),
    path('table1/create/', Table1CreateView.as_view(), name='table1_create'),
    path('table1/<int:pk>/update/', Table1UpdateView.as_view(), name='table1_update'),
    path('table1/<int:pk>/delete/', Table1DeleteView.as_view(), name='table1_delete'),

    # Table2 CRUD
    path('table2/', Table2ListView.as_view(), name='table2_list'),
    path('table2/<int:pk>/', Table2DetailView.as_view(), name='table2_detail'),
    path('table2/create/', Table2CreateView.as_view(), name='table2_create'),
    path('table2/<int:pk>/update/', Table2UpdateView.as_view(), name='table2_update'),
    path('table2/<int:pk>/delete/', Table2DeleteView.as_view(), name='table2_delete'),

    # Table3 CRUD
    path('table3/', Table3ListView.as_view(), name='table3_list'),
    path('table3/<int:pk>/', Table3DetailView.as_view(), name='table3_detail'),
    path('table3/create/', Table3CreateView.as_view(), name='table3_create'),
    path('table3/<int:pk>/update/', Table3UpdateView.as_view(), name='table3_update'),
    path('table3/<int:pk>/delete/', Table3DeleteView.as_view(), name='table3_delete'),
    
    # API endpoints for CRUD operations
    path('api/table1/', Table1APIView.as_view(), name='table1_api'),
    path('api/table2/', Table2APIView.as_view(), name='table2_api'),
    path('api/table3/', Table3APIView.as_view(), name='table3_api'),
    
    # Generic API endpoints
    path('api/generic/table1/', GenericTable1APIView.as_view(), name='generic_table1_api'),
]