from django.urls import path


from .views import LoginView, RegisterView, LogoutView
from . import views

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('register', RegisterView.as_view(), name='register'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('home', views.home, name='home'),

    path('ListView', views.Table1ListView.as_view(), name='list'),
    path('<int:pk>/', views.Table1DetailView.as_view(), name='detail'),
    path('create/', views.Table1CreateView.as_view(), name='create'),
    path('<int:pk>/update/', views.Table1UpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.Table1DeleteView.as_view(), name='delete'),
   #path('register', views.register, name='register'),
   #path('login', views.user_login, name='login'),
   #path('logout', views.user_logout, name='logout'),
   #path('profile', views.profile, name='profile'),
   #path('user_management', views.user_management, name='user_management'),
   #path('user_logs', views.user_logs, name='user_logs'),
    
]