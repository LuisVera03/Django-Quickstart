from django.urls import path

from . import views


urlpatterns = [
    path('',views.index),
    path('crud', views.crud, name='crud'),
    path('get_data', views.get_data, name='get_data'),
    path('add_data', views.add_data, name='add_data'),
    path('update_data', views.update_data, name='update_data'),
    path('delete_data_1', views.delete_data_1, name='delete_data_1'),
    path('delete_data_2', views.delete_data_2, name='delete_data_2'),
]