from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('rest_basic', views.rest_basic, name='rest_basic'),
    path('home_rest_basic', views.home_rest_basic, name='home_rest_basic'),

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

    path('user_register', views.user_register, name='user_register'),
    path('user_login', views.user_login, name='user_login'),
    path('logout', views.user_logout, name='logout'),
    path('profile', views.profile, name='profile'),
    path('user_management', views.user_management, name='user_management'),
    path('user_logs', views.user_logs, name='user_logs'),
    
    path('making_queries', views.making_queries, name='making_queries'),
    path('filter_example', views.filter_example, name='filter_example'),
    path('exclude_example', views.exclude_example, name='exclude_example'),
    path('slice_example', views.slice_example, name='slice_example'),
    path('prefetch_related_example', views.prefetch_related_example, name='prefetch_related_example'),
    path('Q_example', views.Q_example, name='Q_example'),
    path('query_values_example', views.query_values_example, name='query_values_example'),
    path('all_example', views.all_example, name='all_example'),
    path('get_example', views.get_example, name='get_example'),
    path('order_by_example', views.order_by_example, name='order_by_example'),
    path('exists_example', views.exists_example, name='exists_example'),
    path('select_related_example', views.select_related_example, name='select_related_example'),
    path('f_example', views.f_example, name='f_example'),

    path('html_modify', views.html_modify, name='html_modify'),
    path('html_example', views.html_example, name='html_example'),

    path('export_to_file', views.export_to_file, name='export_to_file'),
    path('export_pdf', views.export_pdf, name='export_pdf'),
    path('export_excel', views.export_excel, name='export_excel'),
    
    path('send_email', views.email_send, name='email_send'),
    
    # Test URL - remove in production
    path('test_400', views.test_400, name='test_400'),
    path('test_403', views.test_403, name='test_403'),
    path('test_404', views.test_404, name='test_404'),
    path('test_500', views.test_500, name='test_500'),

]