from django.urls import path

from . import views


urlpatterns = [
    path('',views.index),
    path('rest_basic', views.rest_basic, name='rest_basic'),

    path('crud', views.crud, name='crud'),
    path('get_data', views.get_data, name='get_data'),
    path('add_data', views.add_data, name='add_data'),
    path('update_data', views.update_data, name='update_data'),
    path('delete_data_1', views.delete_data_1, name='delete_data_1'),
    path('delete_data_2', views.delete_data_2, name='delete_data_2'),

    path('crud_form', views.crud_form, name='crud_form'),
    path('get_data_form', views.get_data_form, name='get_data_form'),
    path('form/<str:table>', views.form, name='form'),
    path('update_form/<str:table>/<int:id>', views.update_form, name='update_form'),
    path('add_data_form', views.add_data_form, name='add_data_form'),
    path('update_data_form', views.update_data_form, name='update_data_form'),

    path('user_account', views.user_account, name='user_account'),
    path('register', views.register, name='register'),
    path('login', views.user_login, name='login'),
]