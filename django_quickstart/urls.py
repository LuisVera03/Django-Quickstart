"""django_quickstart URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

#media
from django.conf import settings
from django.conf.urls.static import static

from layer_and_generic import views as layer_and_generic_views
from rest_basic import views as rest_basic_views
from json_app import views as json_app_views
from channels import views as channels_views

urlpatterns = [
    path('', include('rest_basic.urls')),
    path('layer_and_generic/', include('layer_and_generic.urls')),
    path('json_app/', include('json_app.urls')),
    path('channels/', include('channels.urls')),
    path('admin/', admin.site.urls),

    path('layer_and_generic/login/', layer_and_generic_views.LoginView.as_view(), name='login_layer_and_generic'),
    path('json/login/', json_app_views.user_login, name='login_json'),
    path('channels/login/', channels_views.LoginView.as_view(), name='login_channels'),
]

def custom_bad_request_view(request, exception):
    return render(request, 'error_400.html', status=400)

def custom_permission_denied_view(request, exception):
    return render(request, 'error_403.html', status=403)

def custom_page_not_found_view(request, exception):
    return render(request, 'error_404.html', status=404)

def custom_server_error_view(request):
    return render(request, 'error_500.html', status=500)

handler400 = custom_bad_request_view
handler403 = custom_permission_denied_view
handler404 = custom_page_not_found_view
handler500 = custom_server_error_view

#Solo en desarrollo NO en produccion (produccion poner en nginx)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)